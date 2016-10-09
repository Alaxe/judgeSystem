import os
import subprocess

from celery import Task
from django.conf import settings

from .utils import compile_program, init_box, get_box_path, get_sol_path
from judge.models import Solution

class CompileSolution(Task):
    def run(self, solution):
        init_box()
        sourcePath = os.path.join(get_box_path(), 'solution.cpp')

        with open(sourcePath, 'w') as sourceFile:
            sourceFile.write(solution.source)
        
        if not solution.problem.custom_grader:
            status = compile_program(sourcePath, get_sol_path(solution.id))
        else:
            headerName = solution.problem.grader_header_filename

            headerPath = os.path.join(get_box_path(), headerName)
            graderPath = os.path.join(get_box_path(), 'grader.cpp')

            with open(headerPath, 'w') as headerFile:
                headerFile.write(solution.problem.grader_header)

            with open(graderPath, 'w') as graderFile:
                graderFile.write(solution.problem.grader_source)

            status = compile_program(graderPath, get_sol_path(solution.id))

            os.remove(headerPath)
            os.remove(graderPath)

        os.remove(sourcePath)

        solution.compilation_status = status
        solution.save()
