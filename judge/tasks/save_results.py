import os

from celery import Task
from django.db import transaction

from judge.models import TestGroupResult, TestResult, Solution
from .utils import get_sol_path

class SaveResults(Task):
    def save_result_objects(self, results, solution):
        with transaction.atomic():
            failedTestGroups = set()
            
            testGroupResults = {None: None}
            for testGroup in solution.problem.testgroup_set.all():
                testGroupResults[testGroup.pk] = TestGroupResult(
                        test_group = testGroup, solution = solution)

            for testResult in results:
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

            for testResult in results:
                test_group_id = testResult.test.test_group_id
                testResult.test_group_result = testGroupResults[test_group_id]
                testResult.save()

    def run(self, results, solution):
        if solution.compilation_status == Solution.COMPILATION_SUCCEEDED:
            self.save_result_objects(results, solution)
            solution.grader_message = 'Tested'
        elif solution.compilation_status: 
            solution.grader_message = solution.get_compilation_status_display()

        solution.update_score()
        solution.save()

        try:
            os.remove(get_sol_path(solution.id))
        except FileNotFoundError:
            pass
