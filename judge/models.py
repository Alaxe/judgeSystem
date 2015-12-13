from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.dispatch import Signal
from django.utils import timezone

from markdown_deux import markdown
from taggit.managers import TaggableManager

score_field_kwargs = {
    'max_digits': 6, 
    'decimal_places': 2
}

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

    max_score = models.DecimalField(default = 0, **score_field_kwargs)
    visible = models.BooleanField(default = False)
    custom_checker = models.BooleanField(default = False)

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

    def get_tests_by_group(self):
        groupsMap = {}

        testGroups = self.testgroup_set.all()
        tests = self.test_set.all()

        groupsMap[None] = []
        for group in testGroups:
            groupsMap[group.id] = []

        for test in tests:
            groupsMap[test.test_group_id].append(test)
        
        testsByGroup = []
        if groupsMap[None]:
            testsByGroup.append((None, groupsMap[None]))

        for group in testGroups:
            testsByGroup.append((group, groupsMap[group.id]))
        
        return testsByGroup
 
    def update_max_score(self):
        noTestGroup = self.test_set.filter(test_group__isnull = True)
        noTestGroupQ = noTestGroup.aggregate(models.Sum('score'))

        testGroups = self.testgroup_set
        testGroupsQ = testGroups.aggregate(models.Sum('score'))

        self.max_score = 0

        if noTestGroupQ['score__sum']:
            self.max_score += noTestGroupQ['score__sum']
        if testGroupsQ['score__sum']:
            self.max_score += testGroupsQ['score__sum']
        
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

    def __str__(self):
        return self.problem.title + ' --- Solution'

    def get_results_by_group(self):
        testResults = self.testresult_set.all()
        groupResults = self.testgroupresult_set.all()

        groupedResults = {None: []}
        for groupRes in groupResults:
            groupedResults[groupRes.pk] = []

        for testRes in testResults:
            groupedResults[testRes.test_group_result_id].append(testRes)

        resultsByGroup = []
        if groupedResults[None]:
            resultsByGroup.append((None, groupedResults[None]))

        for groupRes in groupResults:
            resultsByGroup.append((groupRes, 
                groupedResults[groupRes.pk]))

        return resultsByGroup


    def update_score(self):
        noTestGroup = self.testresult_set.filter(test__test_group__isnull = True)
        noTestGroupQ = noTestGroup.aggregate(models.Sum('score'))

        testGroups = self.testgroupresult_set.filter(passed = True)
        testGroupsQ = testGroups.aggregate(models.Sum('test_group__score'))

        self.score = 0

        if noTestGroupQ['score__sum']:
            self.score += noTestGroupQ['score__sum']
        if testGroupsQ['test_group__score__sum']:
            self.score += testGroupsQ['test_group__score__sum']

        self.save()

        data = UserProblemData.objects.get(user = self.user, 
            problem = self.problem)

        data.update_score()
        
        statts = UserStatts.objects.get(user = self.user)
        statts.update_statts()

class TestGroup(models.Model):
    name = models.CharField('Name of test group', max_length = 32)
    problem = models.ForeignKey(Problem)
    score = models.DecimalField('Points', **score_field_kwargs)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

class Test(models.Model):
    stdin = models.TextField()
    stdout = models.TextField()

    time_limit = models.DecimalField('Time limit (sec)', **score_field_kwargs)
    mem_limit  = models.IntegerField('Memory limit (MB)')
    score = models.DecimalField('Points', **score_field_kwargs)
    
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

class TestGroupResult(models.Model):
    test_group = models.ForeignKey(TestGroup)
    solution = models.ForeignKey(Solution)

    score = models.DecimalField(default = 0, **score_field_kwargs)
    passed = models.BooleanField(default = True)

    class Meta:
        ordering = ['test_group']

class TestResult(models.Model):
    message = models.CharField(max_length = 64)
    score = models.DecimalField(**score_field_kwargs)
    exec_time = models.CharField(max_length = 16)
    passed = models.BooleanField(default = False)

    solution = models.ForeignKey(Solution)
    test = models.ForeignKey(Test)
    test_group_result = models.ForeignKey(TestGroupResult, null = True)

    class Meta:
        ordering = ['test']


class UserProblemData(models.Model):
    user = models.ForeignKey(User)
    problem = models.ForeignKey(Problem)

    max_score = models.DecimalField(default = 0, **score_field_kwargs)
    last_submit = models.DateTimeField()

    def update_score(self):
        solutions = Solution.objects.filter(user = self.user, 
                        problem = self.problem)
        self.max_score = solutions.aggregate(models.Max('score'))['score__max']
        self.save()

    def __str__(self):
        return self.user.username + ' ' + self.problem.title + ' UPdata'

class UserStatts(models.Model):
    user = models.OneToOneField(User)

    solved_problems = models.IntegerField(default = 0)
    tried_problems = models.IntegerField(default = 0)

    def update_statts(self):
        self.tried_problems = UserProblemData.objects.filter(
                                    user = self.user).count()
        self.solved_problems = UserProblemData.objects.filter(user = self.user,
                                    max_score = F('problem__max_score')).count()
        self.save()

    def __str__(self):
        return self.user.username + '\'s UserStatts'
