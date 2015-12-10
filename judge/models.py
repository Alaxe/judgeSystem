from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.dispatch import Signal
from django.utils import timezone

from markdown_deux import markdown
from taggit.managers import TaggableManager

class Problem(models.Model):
    title = models.CharField('Title', max_length = 64, default="New Problem")

    HTML = 'html'
    MD = 'md'
    STATEMENT_LANGUAGE_CHOICES = (
        (HTML, 'HTML'),
        (MD, 'Markdown'),
    )
    statement_language = models.CharField('Language', max_length = 8,
            choices = STATEMENT_LANGUAGE_CHOICES, default = HTML)
    statement = models.TextField('Problem statement', blank=True)

    maxScore = models.DecimalField(max_digits = 8, decimal_places = 4, default = 0)
    visible = models.BooleanField(default = False)
    customChecker = models.BooleanField(default = False)

    tags = TaggableManager(blank = True)

    class Meta:
        ordering = ['-id']
        permissions = (
            ('problem_retest', 'Can start a retest'),
            ('problem_visibility', 'Can change problem\'s visibility'),
            ('problem_hidden', 'Can see hidden problems'),
            ('add_media_to_problem', 'Can upload media for the problem'),
        )

    def __str__(self):  
        return self.title

    def statement_html(self):
        if self.statement_language == self.MD:
            return markdown(self.statement)
        else:
            return self.statement

    def update_max_score(self):
        noTestGroup = self.test_set.filter(test_group__isnull = True)
        noTestGroupQ = noTestGroup.aggregate(models.Sum('score'))

        testGroups = self.testgroup_set
        testGroupsQ = testGroups.aggregate(models.Sum('score'))

        self.maxScore = noTestGroupQ.get('score__sum', 0) + \
                testGroupsQ.get('score__sum', 0)

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
        noTestGroup = self.testresult_set.filter(test__sub_task__isnull = True)
        noTestGroupQ = noTestGroup.aggregate(models.Sum('score'))

        testGroups = self.testgroupresult_set
        testGroupsQ = testGroups.aggregate(models.Sum('score'))

        self.score = noTestGroupsQ.get('score__sum', 0) + \
            testGroupsQ.get('score__sum', 0)

        self.save()

        data = UserProblemData.objects.get(user = self.user, 
            problem = self.problem)

        data.update_score()
        
        statts = UserStatts.objects.get(user = self.user)
        statts.update()

class TestGroup(models.Model):
    name = models.CharField('Name of test group', max_length = 32)
    problem = models.ForeignKey(Problem)
    score = models.DecimalField('Points', max_digits = 6, decimal_places = 2)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

class TestGroupResult(models.Model):
    test_group = models.ForeignKey(TestGroup)
    solution = models.ForeignKey(Solution)

    score = models.DecimalField('Points', max_digits = 6, decimal_places = 2)

    class Meta:
        ordering = ['test_group']

class Test(models.Model):
    stdin = models.TextField()
    stdout = models.TextField()

    time_limit = models.DecimalField('Time limit (sec)', max_digits = 6,
                                            decimal_places = 4)
    mem_limit  = models.IntegerField('Memory limit (MB)')
    score = models.DecimalField('Points', max_digits = 6, decimal_places = 2)
    
    problem = models.ForeignKey(Problem)
    test_group = models.ForeignKey(TestGroup, null = True, blank = True, 
            on_delete = models.SET_DEFAULT, default = None)

    class Meta:
        permissions = (
            ('view_test', 'Can see input/output files'),
        )
        ordering = ['-test_group', 'pk']

    def __str__(self):
        return self.problem.title + ' --- Test'

class TestResult(models.Model):
    message = models.CharField(max_length = 64)
    score = models.DecimalField(max_digits = 6, decimal_places = 2)
    exec_time = models.CharField(max_length = 16)
    passed = models.BooleanField(default = False)

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
