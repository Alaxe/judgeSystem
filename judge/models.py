import string, random

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
class Problem(models.Model):
    title = models.CharField('Title', max_length = 64)
    statement = models.TextField('Problem statement')

    def __str__(self):  
        return self.title
    
    def get_max_scr(self):
        awns = 0
        for test in self.test_set.all():
            awns += test.points

        return awns

class Solution(models.Model):
    source = models.TextField()
    submit_date = models.DateTimeField('Date of submition')
    grader_message = models.CharField(max_length = 128)

    problem = models.ForeignKey(Problem)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ['-submit_date']

    #To do
    def __str__(self):
        return self.problem.title + ' --- Solution'

    def get_scr(self):
        awns = 0
        for res in self.testresult_set.all():
            awns += res.score
        return awns

class Test(models.Model):
    stdin = models.TextField()
    stdout = models.TextField()

    #time limit in sec and memory limit in kB
    time_limit = models.DecimalField(max_digits = 6, decimal_places = 4)
    mem_limit  = models.IntegerField()
    points = models.IntegerField()
    
    problem = models.ForeignKey(Problem)

    #To do
    def __str__(self):
        return self.problem.title + ' --- Test'

class TestResult(models.Model):
    message = models.CharField(max_length = 64)
    score = models.IntegerField()

    solution = models.ForeignKey(Solution)
    test = models.ForeignKey(Test)

    class Meta:
        ordering = ['test']

def gen_conf_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(32))

class Confirmation(models.Model):
    code = models.CharField(max_length = 32, default = gen_conf_code())
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
