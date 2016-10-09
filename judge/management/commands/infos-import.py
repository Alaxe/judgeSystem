from enum import Enum
import os
import math
import shutil
import subprocess
from urllib.request import urlretrieve
from urllib.error import HTTPError
import zipfile

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from judge.models import Problem, Solution, Test
from judge.tasks import test_solution
from media_manager.models import MediaFile

class Visibility(Enum):
    HIDDEN = 0
    VISIBLE = 1
    FORCE_VISIBLE = 2

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.GROUPS = ['A', 'B', 'C', 'D', 'E']
        #self.GROUPS = ['D']
        self.PROBLEM_PER_GROUP = 3
        self.BASE_URL = 'http://www.math.bas.bg/infos/files/'
        self.ROOT = 'infos-import'

        self.MEMORY_LIMIT = 128
        self.MAX_TIME_LIMIT = 2
        self.PROBLEM_SCORE = 100

    def cleanup(self):
        shutil.rmtree(self.ROOT, ignore_errors = True)

    def setup_directories(self):
        self.cleanup()

        os.makedirs(self.ROOT)

    def download_statements(self, dateStr):
        for group in self.GROUPS:
            for i in range(1, self.PROBLEM_PER_GROUP + 1):
                filename = '{}{}.pdf'.format(group, str(i))
                filepath = os.path.join(self.ROOT, filename)

                url = '{}{}-{}'.format(self.BASE_URL, dateStr, filename)

                urlretrieve(url, filename = filepath)

    def download_tests(self, dateStr):
        for group in self.GROUPS:
            filepath = os.path.join(self.ROOT, '{}-tests.zip'.format(group))
            url = '{}{}-tests&authors-{}.zip'.format(self.BASE_URL, dateStr, group)

            urlretrieve(url, filename = filepath)
            with zipfile.ZipFile(filepath, 'r') as zipRef:
                zipRef.extractall(self.ROOT)

    def get_problem_name(self, group, ind):
        for f in os.listdir(path = os.path.join(self.ROOT, group)):
            if f.startswith(str(ind) + '-'):
                return f[2:]

        return None

    def add_tests(self, problem, path):
        testFilenames = os.listdir(path = path)
        testFilenameSet = set(testFilenames)

        inputExtensions = ['.in', '.txt', '.test']
        outputExtensions = ['.sol', '.out', '.ok']

        testCount = 0
        for inputFilename in sorted(testFilenames):
            testBase = None
            for ext in inputExtensions:
                if inputFilename.endswith(ext):
                    testBase = inputFilename[:-len(ext)]
                    break

            if not testBase:
                continue

            outputFilename = None
            for ext in outputExtensions:
                if testBase + ext in testFilenameSet:
                    outputFilename = testBase + ext
                    break

            if not outputFilename:
                continue

            test = Test(problem = problem, time_limit = self.MAX_TIME_LIMIT,
                    mem_limit = self.MEMORY_LIMIT, score = 1)

            with open(os.path.join(path, inputFilename)) as inputFile:
                test.stdin = inputFile.read()

            with open(os.path.join(path, outputFilename)) as outputFile:
                test.stdout = outputFile.read()
            
            testCount += 1
            test.save()
        
        if testCount:
            scorePerTest = self.PROBLEM_SCORE / testCount
            Test.objects.filter(problem = problem).update(score = scorePerTest)

    def get_user_by_username(self, username):
        try:
            return User.objects.get(username = username)
        except User.DoesNotExist:
            return User.objects.create_user(username)

    def find_potential_solutions(self, problem, path, user):
        solutions = []

        for node in os.walk(path):
            directory = node[0]

            for filename in node[2]:
                if filename.endswith('.cpp'):
                    source = ''
                    with open(os.path.join(directory, filename)) as f:
                        source = f.read()

                    solutions.append(Solution.objects.create(user = user,
                        source = source, problem = problem))

        return solutions

    def time_author_solutions(self, solutions):
        minTime = None
        for sol in solutions:
            test_solution(sol).delay().get()
            sol.refresh_from_db()

            if not math.isclose(sol.score, sol.problem.max_score):
                continue

            curTime = max(float(res.exec_time) for res in sol.testresult_set.all())
            if (not minTime) or (minTime > curTime):
                minTime = curTime

        return minTime

    def determine_timelimit(self, problem, path, **options):
        print('Testing {}...'.format(problem.title))

        user = self.get_user_by_username(options['user'])
        solutions = self.find_potential_solutions(problem, path, user)

        worst_time = self.time_author_solutions(solutions)
        if not worst_time:
            return None

        time_limit = math.ceil(worst_time * 2 * 10) / 10
        if time_limit > self.MAX_TIME_LIMIT:
            time_limit = self.MAX_TIME_LIMIT

        Test.objects.filter(problem = problem).update(time_limit = time_limit)
        #retest_problem(problem).delay()

        return time_limit

    def add_problem(self, group, ind, **options):
        name = self.get_problem_name(group, ind)
        problem = Problem.objects.create(title = name.capitalize())
        path = os.path.join(self.ROOT, group, '{}-{}'.format(ind, name))

        self.add_tests(problem, os.path.join(path, 'tests'))
        problem.update_max_score()

        pdfLink = ''
        pdfPath = os.path.join(self.ROOT, '{}{}.pdf'.format(group, str(ind)))
        with open(pdfPath, 'rb') as pdf:
            media = MediaFile(content_object = problem, 
                    filename = '{}{}-statement.pdf'.format(group, str(ind)),
                    media = File(pdf))
            media.save()

        timelimit = self.determine_timelimit(problem, path, **options)


        if options['visibility'] == Visibility.HIDDEN:
            problem.visible = False
        elif options['visibility'] == Visibility.FORCE_VISIBLE:
            problem.visible = True
        else:
            problem.visible = (timelimit != None)

        if not timelimit:
            timelimit = self.MAX_TIME_LIMIT

        problem.statement = ('**Statement:** [PDF]({}) \n\n' + \
            '**Time limit**: {} s\n\n' + \
            '**Memorylimit**: {} MB\n\n')\
            .format(media.media.url, timelimit, self.MEMORY_LIMIT)
        problem.statement_language = Problem.MD

        problem.tags.add(group, options['competition-date'][:4],
                *options['tags'])

        problem.save()

    def add_arguments(self, parser):
        parser.add_argument('competition-date', 
                type = str,
                help = 'The date of the imported competition, in format \
                        yyyy-mm-dd. Used for generation of URL\'s at \
                        http://math.bas.bg/infos/ .'
                )

        parser.add_argument('--tags', 
                dest = 'tags', 
                type = str, 
                nargs = '*',
                default = [], 
                help = 'Addititonal tags to be added to the problems. Useful \
                        for a competiton specific tag.'
                )

        parser.add_argument('--keep', 
                dest = 'cleanup', 
                action = 'store_false',
                default = True, 
                help = 'Use this option to keep the working files. (by \
                        default they\'re deleted)'
                )

        parser.add_argument('--user', 
                dest = 'user', 
                type = str,
                default = 'infos', 
                help = 'The user used when testing the author solutions. If \
                        the specified user doesn\'t exist, they will be \
                        created.'
                )

        parser.add_argument('--hidden', 
                dest = 'visibility', 
                action = 'store_const', 
                const = Visibility.HIDDEN,
                default = Visibility.VISIBLE, 
                help = 'All added problems are hidden. By default they are \
                        vissible unless an error occurs.'
                )
        parser.add_argument('--visible',
                dest = 'visibility',
                action = 'store_const',
                const = Visibility.VISIBLE,
                default = Visibility.VISIBLE,
                help = 'All added problems are visible, unless an error occurs. \
                        This is the default behaviour.'
                )
        parser.add_argument('--force-visible',
                dest = 'visibility',
                action = 'store_const',
                const = Visibility.FORCE_VISIBLE,
                default = Visibility.VISIBLE,
                help = 'All added problems are visible, even if errors occur.')

    def handle(self, *args, **options):
        self.setup_directories()

        print('Downloading competition data...')
        try:
            self.download_statements(options['competition-date'])
            self.download_tests(options['competition-date'])

            print('Adding problems...')
            for group in self.GROUPS:
                for i in range(1, self.PROBLEM_PER_GROUP + 1):
                    self.add_problem(group, i, **options)

        except HTTPError as err:
            print(err)
            print('An error has occured while downloading the problems.')
            print('Make sure you have provided a correct competition date.')

        finally:
            if options['cleanup']:
                print('Cleaning up...')
                self.cleanup()
