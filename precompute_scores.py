from judge.models import Solution, UserProblemData
from users.models import UserStatts

print('cleaning up')
for statt in UserStatts.objects.all():
    statt.triedProblems = 0
    statt.solvedProblems = 0
    statt.save()

for data in UserProblemData.objects.all():
    data.delete()

print('evaluating scores')

for sol in Solution.objects.all() :
    sol.update_score()
    if sol.id % 20 == 0:
        print(sol.id)


