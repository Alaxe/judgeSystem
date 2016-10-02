import os
import urllib.request
import shutil
import subprocess
import zipfile

from django.core.management.base import BaseCommand, CommandError

from judge.models import Problem, Test

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.GROUPS = ['A', 'B', 'C', 'D', 'E']
        self.PROBLEM_PER_GROUP = 3
        self.BASE_URL = 'http://www.math.bas.bg/infos/files/'

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

        self.download_statements(options['competition-date'])
        self.download_tests(options['competition-date'])

        if options['cleanup']:
            self.cleanup()
