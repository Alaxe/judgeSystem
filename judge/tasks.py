from __future__ import absolute_import

from celery import shared_task
from billiard import current_process
from django.core.cache import cache
from .models import Test, TestResult, Solution

import subprocess, time, os

def get_sol_loc(solution):
    solutionRoot = 'judge/solutions/'
    return solutionRoot + str(solution.pk) + '-run'
def get_box_id():
    return current_process().index
def get_box_loc():
    return '/tmp/box/' + str(get_box_id()) + '/box/'
def get_sandbox():
    return 'judge/isolate'


def compile_solution(solution):
    sourceFile = open('source.cpp', 'w')
    sourceFile.write(solution.source)
    sourceFile.close()

    compileArgs = ['g++', '-O2', '--std=c++11',
                    '-o', get_sol_loc(solution), 'source.cpp']

    returnCode = subprocess.call(compileArgs)
    os.remove('source.cpp')

    return (returnCode == 0)

def setup_box(solution, test):
    sandbox = get_sandbox()
    boxId = get_box_id()
    subprocess.call([sandbox, '-b', str(boxId), '--init'])
    subprocess.call(['cp', get_sol_loc(solution), 
                    get_box_loc() + 'solution'])

    inFilePath = get_box_loc() + 'std.in'
    inFile = open(inFilePath, 'w')
    inFile.write(test.stdin)
    inFile.close()

def run_solution(test):
    sandbox = get_sandbox()
    boxId = get_box_id()
    args = [sandbox, '-i', 'std.in', '-o', 'std.out',
            '-b', str(boxId), '-t', str(test.time_limit), '-m', 
            str(test.mem_limit * 1024), '--run', 'solution']

    proc = subprocess.Popen(args, stdout = subprocess.PIPE, 
                            stderr = subprocess.PIPE)
    while proc.poll():
        time.sleep(0.001)

    out, err = proc.communicate()
    return err.decode('utf-8')

def check_output(test):
    outFilePath = get_box_loc() + 'std.out'
    outFile = open(outFilePath, 'r')
    curOut = outFile.read()
    curOut = curOut.replace('\n', '\r\n')
    outFile.close()

    corOut = test.stdout
    print(bytes(curOut, 'utf-8'))
    print(bytes(corOut, 'utf-8'))

    #print ('cur ' + curOut)
    #print ('cor ' + corOut)

    return curOut == corOut 

def test_finished(solution):
    testCnt = solution.problem.test_set.count()
    resultCnt = solution.testresult_set.count()

    return resultCnt == testCnt

@shared_task
def test_solution(solution):
    if not compile_solution(solution):
        solution.grader_message = 'Compilation error'
        solution.save()
        return
    
    solution.grader_message = 'Testing'
    solution.save()

    for t in solution.problem.test_set.all():
        run_test.delay(solution, t)

@shared_task
def run_test(solution, test):
    boxId = get_box_id()
    
    setup_box(solution, test)
    sandbox_msg = run_solution(test)
    score = 0
    if sandbox_msg[:2] == 'OK' :
        msg = 'wrong awnser'
        
        if check_output(test):
            msg = 'correct'
            score = test.points

        sandbox_msg = msg + sandbox_msg[2:]
    
    result = TestResult(message = sandbox_msg, score = score,
                        solution = solution, test = test)
    result.save()
    
    if test_finished(solution):
        os.remove(get_sol_loc(solution))
        solution.grader_message = 'Tested'
        solution.save()

