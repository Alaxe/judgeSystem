from __future__ import absolute_import

import os
import time
import signal
import subprocess
import sys

from billiard import current_process
from celery import shared_task
from celery.task import chord, group
from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from judge.models import Test, TestResult, TestGroupResult, Solution, \
        UserProblemData, UserStats

sandbox = 'isolate'

def get_sol_loc(solution_id):
    solutionRoot = settings.BASE_DIR + '/judge/solutions/'
    return solutionRoot + str(solution_id)
def get_box_id():
    return current_process().index
def get_box_loc():
    return '/var/local/lib/isolate/' + str(get_box_id()) + '/box/'
def get_grader_loc(problem):
    return settings.BASE_DIR + '/judge/graders/' + str(problem.pk)
def init_box():
    subprocess.call([sandbox, '-b', str(get_box_id()), '--init'])


def compile_program(sourcePath, destPath):
    compileArgs = ['g++', '-O2', '--std=c++11', '-o', destPath, sourcePath]
    try:
        proc = subprocess.Popen(compileArgs, preexec_fn = os.setsid)
        if proc.wait(timeout = settings.JUDGE_COMPILE_TL) != 0:
            raise subprocess.CalledProcessError(proc.returncode, 'g++')
    except subprocess.TimeoutExpired as e:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        raise e
    finally:
        os.remove(sourcePath)

def compile_solution(solution):
    init_box()

    sourcePath = get_box_loc() + 'solution.cpp'

    with open(sourcePath, 'w') as sourceFile:
        sourceFile.write(solution.source)
    
    if not solution.problem.custom_grader:
        compile_program(sourcePath, get_sol_loc(solution.id))
    else:
        headerPath = get_box_loc() + solution.problem.grader_header_filename
        graderPath = get_box_loc() + 'grader.cpp'

        with open(headerPath, 'w') as headerFile:
            headerFile.write(solution.problem.grader_header)

        with open(graderPath, 'w') as graderFile:
            graderFile.write(solution.problem.grader_source)

        try:
            compile_program(graderPath, get_sol_loc(solution.id))
        finally:
            os.remove(sourcePath)
            os.remove(headerPath)
    
def setup_box_for_test(solution_id, test):
    init_box()
    subprocess.call(['cp', get_sol_loc(solution_id), 
                    get_box_loc() + 'solution'])

    inFilePath = get_box_loc() + 'std.in'

    with open(inFilePath, 'w') as inFile:
        inFile.write(test.stdin)

def run_solution(test):
    boxId = get_box_id()
    time_limit = str(test.time_limit)

    args = [sandbox, '-i', 'std.in', '-o', 'std.out', '-b', str(boxId), 
            '-t', time_limit, '-m', str(test.mem_limit * 1024), 
            '--run', 'solution']

    proc = subprocess.Popen(args, stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE)
    proc.wait()
    out, err = proc.communicate()
    return err.decode('utf-8')

def check_output(test):
    if test.problem.custom_checker:
        return custom_grader(test)
    else:
        return default_grader(test)

def default_grader(test):
    outFilePath = get_box_loc() + 'std.out'

    with open(outFilePath, 'r') as outFile:
        curOut = outFile.read().split()
        corOut = test.stdout.split()

        return curOut == corOut 
    return 0

def custom_grader(test):
    problem = test.problem

    inFilePath = get_box_loc() + 'std.in'
    outFilePath = get_box_loc() + 'std.out'
    correctFilePath = get_box_loc() + 'cor.out'
    graderFilePath = get_box_loc() + 'grader'

    with open(correctFilePath, 'w') as correctFile:
        correctFile.write(test.stdout)

    subprocess.call(['cp', get_grader_loc(problem), graderFilePath])
    subprocess.call(['chmod', '700', graderFilePath])
    scoreMessage = subprocess.check_output([graderFilePath, inFilePath, 
            correctFilePath, outFilePath])

    score = float(scoreMessage.split()[0])

    return score


@shared_task(ignore_result = True) 
def test_solution(solution):
    try:
        compile_solution(solution)
        solution.grader_message = 'Testing'

        taskList = []
        print('adding tests')
        print(sys.getsizeof(solution))
        tests = Test.objects.filter(problem_id = solution.problem_id)
        for t in tests:
            curSubTask = run_test.si(solution.id, t.id)
            taskList.append(curSubTask)

        res = chord(group(taskList), save_result.s(solution))
        res.apply_async()
        print('tests added')

    except subprocess.CalledProcessError:
        solution.grader_message = 'Compilation error (syntax)'
    except subprocess.TimeoutExpired:
        solution.grader_message = 'Compilation error (timeout)'
    finally:
        solution.save()
    
@shared_task
def run_test(solution_id, test_id):
    test = Test.objects.get(id = test_id)
    boxId = get_box_id()
    
    setup_box_for_test(solution_id, test)
    sandbox_msg = run_solution(test)

    score = 0
    time = 'N\\A'
    passed = False

    if sandbox_msg[:2] == 'OK' :
        msg = 'Wrong awnser'
        time = sandbox_msg[4:9]
        
        if check_output(test):
            msg = 'Accepted'
            score = test.score
            passed = True


        sandbox_msg = msg
    
    result = TestResult(message = sandbox_msg, score = score, passed = passed,
                        solution_id = solution_id, test_id = test.id, exec_time = time)
    return result

@shared_task(ignore_result = True) 
def save_result(result, solution):
    print('save reuslts')
    with transaction.atomic():
        failedTestGroups = set()
        
        testGroupResults = {None: None}
        for testGroup in solution.problem.testgroup_set.all():
            testGroupResults[testGroup.pk] = TestGroupResult(
                    test_group = testGroup, solution = solution)

        for testResult in result:
            if not testResult.passed:
                failedTestGroups.add(testResult.test.test_group_id)


        for groupId, groupResult in testGroupResults.items():
            if not groupId:
                continue

            if groupId in failedTestGroups:
                groupResult.passed = False
                groupResult.score = 0
            else:
                groupResult.passed = True
                groupResult.score = groupResult.test_group.score

            groupResult.save()

        for testResult in result:
            test_group_id = testResult.test.test_group_id
            testResult.test_group_result = testGroupResults[test_group_id]
            testResult.save()

    solution.grader_message = 'Tested'
    solution.update_score()
    solution.save()

    try:
        os.remove(get_sol_loc(solution.id))
    except FileNotFoundError:
        pass

@shared_task(ignore_result = True) 
def retest_problem(problem):
    solutions = problem.solution_set.all()

    with transaction.atomic():
        UPdata = UserProblemData.objects.filter(problem = problem)

        for sol in solutions:
            sol.testresult_set.all().delete()
            sol.testgroupresult_set.all().delete()
            sol.score = 0
            sol.grader_message = 'In Queue'
            sol.save()

            test_solution.delay(sol)

        for data in UPdata:
            data.max_score = 0
            data.save()
            UserStats.get_for_user(data.user).update()
