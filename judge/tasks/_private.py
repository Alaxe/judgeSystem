import os
import subprocess

from billiard import current_process
from django.conf import settings

SOLUTION_ROOT = settings.BASE_DIR +'/judge/solutions'
GRADER_ROOT = settings.BASE_DIR + '/judge/graders' 

SANDBOX = 'isolate'
SANDBOX_ROOT ='/var/local/lib/isolate' 

def get_box_id():
    return current_process().index

def get_sol_path(solution_id):
    return os.path.join(SOLUTION_ROOT, str(solution_id))

def get_box_path():
    return os.path.join(SANDBOX_ROOT, str(get_box_id()), 'box')

def get_grader_path(problem):
    return os.path.join(GRADER_ROOT, str(problem.pk))

def init_box():
    subprocess.call([SANDBOX, '-b', str(get_box_id()), '--init'])


