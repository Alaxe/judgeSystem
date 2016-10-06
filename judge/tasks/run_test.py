import os
import subprocess

from celery import Task

from ._private import init_box, get_box_id, get_box_path, get_grader_path, \
        get_sol_path, SANDBOX
from judge.models import Test, TestResult

class RunTest(Task):
    def setup_box_for_test(self, solution_id, test):
        init_box()
        subprocess.call(['cp', get_sol_path(solution_id), 
                        os.path.join(get_box_path(), 'solution')])

        inFilePath = os.path.join(get_box_path(), 'std.in')

        with open(inFilePath, 'w') as inFile:
            inFile.write(test.stdin)

    def run_solution(self, test):
        boxId = get_box_id()
        time_limit = str(test.time_limit)

        args = [SANDBOX, '-i', 'std.in', '-o', 'std.out', '-b', str(boxId), 
                '-t', time_limit, '-m', str(test.mem_limit * 1024), 
                '--run', 'solution']

        proc = subprocess.Popen(args, stdout = subprocess.PIPE, 
                                stderr = subprocess.PIPE)
        proc.wait()
        out, err = proc.communicate()
        return err.decode('utf-8')

    def default_grader(self, test):
        outFilePath = os.path.join(get_box_path(), 'std.out')

        with open(outFilePath, 'r') as outFile:
            curOut = outFile.read().split()
            corOut = test.stdout.split()

            return curOut == corOut 
        return 0

    def custom_grader(self, test):
        problem = test.problem

        inFilePath = os.path.join(get_box_path(), 'std.in')
        outFilePath = os.path.join(get_box_path(), 'std.out')
        correctFilePath = os.path.join(get_box_path(), 'cor.out')
        graderFilePath = os.path.join(get_box_path(), 'grader')

        with open(correctFilePath, 'w') as correctFile:
            correctFile.write(test.stdout)

        subprocess.call(['cp', get_grader_path(problem), graderFilePath])
        subprocess.call(['chmod', '700', graderFilePath])
        scoreMessage = subprocess.check_output([graderFilePath, inFilePath, 
                correctFilePath, outFilePath])

        score = float(scoreMessage.split()[0])

        return score

    def check_output(self, test):
        if test.problem.custom_checker:
            return self.custom_grader(test)
        else:
            return self.default_grader(test)


    def run(self, solution_id, test_id):
        #The solution hasn't compiled
        if not os.path.isfile(get_sol_path(solution_id)):
            return None
        
        test = Test.objects.get(id = test_id)
        boxId = get_box_id()
        
        self.setup_box_for_test(solution_id, test)
        sandbox_msg = self.run_solution(test)

        score = 0
        time = 'N\\A'
        passed = False

        if sandbox_msg[:2] == 'OK' :
            msg = 'Wrong awnser'
            time = sandbox_msg[4:9]
            
            if self.check_output(test):
                msg = 'Accepted'
                score = test.score
                passed = True


            sandbox_msg = msg
        
        result = TestResult(message = sandbox_msg, score = score, passed = passed,
                            solution_id = solution_id, test_id = test.id, exec_time = time)
        return result
