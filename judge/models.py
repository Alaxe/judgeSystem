from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.dispatch import Signal
from django.utils import timezone

from taggit.managers import TaggableManager

class Problem(models.Model):
    title = models.CharField('Title', max_length = 64)
    statement = models.TextField('Problem statement')
    maxScore = models.DecimalField(max_digits = 8, decimal_places = 4, default = 0)
    visible = models.BooleanField(default = False)
    customChecker = models.BooleanField(default = False)

    tags = TaggableManager(blank = True)

    class Meta:
        ordering = ['-id']
        permissions = (
            ('problem_retest', 'Can start a retest'),
            ('problem_visibility', 'Can change problem\'s visibility'),
            ('problem_hidden', 'Can see hidden problems')
        )

    def __str__(self):  
        return self.title

    def update_max_score(self):
        query = self.test_set.aggregate(models.Sum('score'))
        print(query)
        self.maxScore = query['score__sum']
        self.save()
    
class Solution(models.Model):
    source = models.TextField()
    submit_date = models.DateTimeField('Date of submition')

    grader_message = models.CharField(max_length = 32)

    problem = models.ForeignKey(Problem)
    user = models.ForeignKey(User)
    score = models.DecimalField(max_digits = 8, decimal_places = 4, default = 0)

    class Meta:
        ordering = ['-submit_date']
        permissions = (
            ('view_foreign_solution', 'Can see somebody else\'s solution'),
        )

    #To do
    def __str__(self):
        return self.problem.title + ' --- Solution'

    def update_score(self):
        query = self.testresult_set.aggregate(models.Sum('score'))
        self.score = query['score__sum']
        self.save()

        data = UserProblemData.objects.get(user = self.user,
                                        problem = self.problem)

        data.update_score()
        
        statts = UserStatts.objects.get(user = self.user)
        statts.update()

class Test(models.Model):
    stdin = models.TextField()
    stdout = models.TextField()

    #time limit in sec and memory limit in kB
    time_limit = models.DecimalField(max_digits = 6, decimal_places = 4)
    mem_limit  = models.IntegerField()
    score = models.DecimalField(max_digits = 8, decimal_places = 4)
    
    problem = models.ForeignKey(Problem)

    class Meta:
        permissions = (
            ('view_test', 'Can see input/output files'),
        )
        ordering = ['pk']

    def __str__(self):
        return self.problem.title + ' --- Test'

class TestResult(models.Model):
    message = models.CharField(max_length = 64)
    score = models.DecimalField(max_digits = 8, decimal_places = 4)
    exec_time = models.CharField(max_length = 16)

    solution = models.ForeignKey(Solution)
    test = models.ForeignKey(Test)

    class Meta:
        ordering = ['test']


class UserProblemData(models.Model):
    user = models.ForeignKey(User)
    problem = models.ForeignKey(Problem)

    maxScore = models.DecimalField(max_digits = 8, decimal_places = 4, 
                                default = 0)
    last_submit = models.DateTimeField()

    def update_score(self):
        solutions = Solution.objects.filter(user = self.user, 
                        problem = self.problem)
        self.maxScore = solutions.aggregate(models.Max('score'))['score__max']
        self.save()

    def __str__(self):
        return self.user.username + ' ' + self.problem.title + ' UPdata'

class UserStatts(models.Model):
    user = models.OneToOneField(User)

    solvedProblems = models.IntegerField(default = 0)
    triedProblems = models.IntegerField(default = 0)

    def update(self):
        self.triedProblems = UserProblemData.objects.filter(
                                    user = self.user).count()
        self.solvedProblems = UserProblemData.objects.filter(user = self.user,
                                    maxScore = F('problem__maxScore')).count()
        self.save()

    def __str__(self):
        return self.user.username + '\'s UserStatts'
