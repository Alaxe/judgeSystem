from judge.models import Problem 
from judge.tasks import retest_problem

print("hi")
for p in Problem.objects.all():
    print(p.id)
    retest_problem(p)
