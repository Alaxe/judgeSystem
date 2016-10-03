import os
import urllib.request
import shutil
import subprocess
import zipfile

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from judge.models import Problem, Test
from media_manager.models import MediaFile

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        #self.GROUPS = ['A', 'B', 'C', 'D', 'E']
        self.GROUPS = ['B']
        self.PROBLEM_PER_GROUP = 3
        self.BASE_URL = 'http://www.math.bas.bg/infos/files/'

        self.MEMORY_LIMIT = 128
        self.BASE_TIME_LIMIT = 1
        self.PROBLEM_SCORE = 100

    def cleanup(self):
        shutil.rmtree('download', ignore_errors = True)
        shutil.rmtree('task', ignore_errors = True)

    def setup_directories(self):
        self.cleanup()

        os.makedirs('download')
        os.makedirs('task')

    def download_statements(self, dateStr):
        for group in self.GROUPS:
            for i in range(1, self.PROBLEM_PER_GROUP + 1):
                filename = '{}{}.pdf'.format(group, str(i))
                filepath = 'download/{}'.format(filename)

                url = '{}{}-{}'.format(self.BASE_URL, dateStr, filename)

                urllib.request.urlretrieve(url, filename = filepath)

    def download_tests(self, dateStr):
        for group in self.GROUPS:
            filepath = 'download/{}-tests.zip'.format(group)
            url = '{}{}-tests&authors-{}.zip'.format(self.BASE_URL, dateStr, group)

            urllib.request.urlretrieve(url, filename = filepath)
            with zipfile.ZipFile(filepath, 'r') as zipRef:
                zipRef.extractall('download/')

    def get_problem_name(self, group, ind):
        for f in os.listdir(path = 'download/' + group):
            if f.startswith(str(ind) + '-'):
                return f[2:]

        return None

    def add_tests(self, problem, path):
        testFilenames = os.listdir(path = path)
        testFilenameSet = set(testFilenames)

        inputExtensions = ['.in', '.txt', '.test']
        outputExtensions = ['.sol', '.out', '.ok']

        testCount = 0
        for inputFilename in testFilenames:
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

            test = Test(problem = problem, time_limit = self.BASE_TIME_LIMIT,
                    mem_limit = self.MEMORY_LIMIT, score = 1)

            with open(path + inputFilename) as inputFile:
                test.stdin = inputFile.read()

            with open(path + outputFilename) as outputFile:
                test.stdout = outputFile.read()

            test.save()
            testCount += 1
        
        if testCount:
            scorePerTest = self.PROBLEM_SCORE / testCount
            Test.objects.filter(problem = problem).update(score = scorePerTest)

        print('{} - {}'.format(problem.title, testCount))


    def add_problem(self, group, ind):
        name = self.get_problem_name(group, ind)
        problem = Problem.objects.create(title = name.capitalize())

        pdfLink = ''
        with open('download/{}{}.pdf'.format(group, str(ind)), 'rb') as pdf:
            media = MediaFile(content_object = problem, 
                    filename = '{}{}-statement.pdf'.format(group, str(ind)),
                    media = File(pdf))
            media.save()

        problem.statement = '[PDF]({})'.format(media.media.url)
        problem.statement_language = Problem.MD

        problem.save()

        self.add_tests(problem, 
                'download/{}/{}-{}/tests/'.format(group, ind, name))
        problem.update_max_score()

    def add_arguments(self, parser):
        parser.add_argument('competition-date', type=str,
                help = 'The date of the imported competition, in format \
                yyyy-mm-dd. Used for generation of URL\'s at \
                http://math.bas.bg/infos/')

        parser.add_argument('--keep', dest = 'cleanup', action = 'store_false',
                default = True, help = 'Use this option to keep the working \
                files. (by default they\'re deleted)')

    def handle(self, *args, **options):
        self.setup_directories()

        print('Downloading competition data...')
        self.download_statements(options['competition-date'])
        self.download_tests(options['competition-date'])

        print('Adding problems...')
        for group in self.GROUPS:
            for i in range(1, self.PROBLEM_PER_GROUP + 1):
                self.add_problem(group, i)

        if options['cleanup']:
            print('Cleaning up...')
            self.cleanup()
