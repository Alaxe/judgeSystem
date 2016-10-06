import os
import subprocess

from celery import Task
from django.conf import settings

from ._private import init_box, get_box_path, get_sol_path
from judge.models import Solution

class CompileSolution(Task):
    def compile_program(self, sourcePath, destPath):
        compileArgs = ['g++', '-O2', '--std=c++11', '-o', destPath, sourcePath]

        try:
            proc = subprocess.Popen(compileArgs, preexec_fn = os.setsid)

            if proc.wait(timeout = settings.JUDGE_COMPILE_TL) == 0:
                return Solution.COMPILATION_SUCCEEDED
            else:
                return Solution.COMPILATION_FAILED_SYNTAX

        except subprocess.TimeoutExpired as e:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            return Solution.COMPILATION_FAILED_TL

    def run(self, solution):
        init_box()
        sourcePath = os.path.join(get_box_path(), 'solution.cpp')

        with open(sourcePath, 'w') as sourceFile:
            sourceFile.write(solution.source)
        
        if not solution.problem.custom_grader:
            status = self.compile_program(sourcePath, get_sol_path(solution.id))
        else:
            headerName = solution.problem.grader_header_filename

            headerPath = os.path.join(get_box_path(), headerName)
            graderPath = os.path.join(get_box_path(), 'grader.cpp')

            with open(headerPath, 'w') as headerFile:
                headerFile.write(solution.problem.grader_header)

            with open(graderPath, 'w') as graderFile:
                graderFile.write(solution.problem.grader_source)

            status = self.compile_program(graderPath, get_sol_path(solution.id))

            os.remove(headerPath)
            os.remove(graderPath)

        os.remove(sourcePath)

        solution.compilation_status = status
        solution.save()
