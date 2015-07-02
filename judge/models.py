from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from users.models import UserStatts

class Problem(models.Model):
    title = models.CharField('Title', max_length = 64)
    statement = models.TextField('Problem statement')
    maxScore = models.IntegerField(default = 0)

    class Meta:
        ordering = ['-id']
        permissions = (
            ('retest_problem', 'Can start a retest'),
        )

    def __str__(self):  
        return self.title

    def update_max_score(self):
        awns = 0
        for test in self.test_set.all():
            awns += test.points

        self.maxScore = awns
        self.save()
    
class Solution(models.Model):
    source = models.TextField()
    submit_date = models.DateTimeField('Date of submition')

    grader_message = models.CharField(max_length = 32)

    problem = models.ForeignKey(Problem)
    user = models.ForeignKey(User)
    score = models.IntegerField(default = 0)

    class Meta:
        ordering = ['-submit_date']
        permissions = (
            ('view_foreign_solution', 'Can see somebody else\'s solution'),
        )

    #To do
    def __str__(self):
        return self.problem.title + ' --- Solution'

    def update_score(self):
        self.score = 0
        for res in self.testresult_set.all():
            self.score += res.score
        self.save()

        userStatts = UserStatts.objects.get(user = self.user)
        data = UserProblemData.objects.get(user = self.user,
                                            problem = self.problem)

        if data.maxScore < self.score :
            data.maxScore = self.score
            data.save()

            if data.maxScore == self.problem.maxScore :
                userStatts.solvedProblems += 1
                userStatts.save()

class Test(models.Model):
    stdin = models.TextField()
    stdout = models.TextField()

    #time limit in sec and memory limit in kB
    time_limit = models.DecimalField(max_digits = 6, decimal_places = 4)
    mem_limit  = models.IntegerField()
    points = models.IntegerField()
    
    problem = models.ForeignKey(Problem)

    class Meta:
        permissions = (
            ('view_test', 'Can see input/output files'),
        )

    def __str__(self):
        return self.problem.title + ' --- Test'

    def save(self, *args, **kwargs):
        self.problem.update_max_score()
        super(Test, self).save(*args, **kwargs)

class TestResult(models.Model):
    message = models.CharField(max_length = 64)
    score = models.IntegerField()
    exec_time = models.CharField(max_length = 16)

    solution = models.ForeignKey(Solution)
    test = models.ForeignKey(Test)

    class Meta:
        ordering = ['test']


class UserProblemData(models.Model):
    user = models.ForeignKey(User)
    problem = models.ForeignKey(Problem)

    maxScore = models.IntegerField(default = 0)
    last_submit = models.DateTimeField()
