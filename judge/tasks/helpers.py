from celery import group, Task, chord
from django.db import transaction

from judge.models import Solution, Test, UserProblemData, UserStats

from judge.tasks.compile_solution import CompileSolution
from judge.tasks.run_test import RunTest
from judge.tasks.save_results import SaveResults

def test_solution(solution):
    solution.grader_message = 'Testing'
    solution.save()

    compileTask = CompileSolution().si(solution)


    tests = Test.objects.filter(problem_id = solution.problem_id)
    testTasks = []
    for t in tests:
        testTasks.append(RunTest().si(solution.id, t.id))

    saveTask = SaveResults().s(solution)

    return (compileTask | group(testTasks) | saveTask)

def retest_problem(problem):
    solutions = problem.solution_set.all()

    tasks = []
    with transaction.atomic():
        UPdata = UserProblemData.objects.filter(problem = problem)

        for sol in solutions:
            sol.testresult_set.all().delete()
            sol.testgroupresult_set.all().delete()
            sol.score = 0
            sol.grader_message = 'In Queue'
            sol.save()

            tasks.append(test_solution(sol))

        for data in UPdata:
            data.max_score = 0
            data.save()
            UserStats.get_for_user(data.user).update()

    return group(tasks)
