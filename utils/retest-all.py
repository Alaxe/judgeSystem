from judge.models import Problem 
from judge.tasks import retest_problem

for p in Problem.objects.all():
    retest_problem(p)

