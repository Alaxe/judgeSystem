from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django import forms
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View

from judge.models import Problem, Test, TestGroup

from zipfile import ZipFile, BadZipFile
import os

class TestEditForm(forms.ModelForm):
    stdinFile = forms.FileField(label = 'Input file', required=False)
    stdoutFile = forms.FileField(label = 'Output file',required=False)

    class Meta:
        model = Test
        exclude = ['stdin', 'stdout', 'problem', 'test_group']

    def is_valid(self, update=False):
        valid = super(TestEditForm, self).is_valid()
        
        if update:
            return valid

        if self.cleaned_data['stdinFile'] == None:
            self.add_error('stdinFile', 'Include input File')
            valid = False

        if self.cleaned_data['stdoutFile'] == None:
            self.add_error('stdoutFile', 'Include output file')
            valid = False

        return valid

class TestNewForm(TestEditForm):
    zipFile = forms.FileField(label = 'Test archive(zip)', required = False)

    def is_valid(self):
        super(TestEditForm, self).is_valid()

        update = False

        if self.cleaned_data['zipFile'] != None:
            update = True
    
        valid = super(TestNewForm, self).is_valid(update = update)
        if not valid:
            self.add_error('zipFile', 'No zipfile uploaded')

        return valid

class TestNew(View):
    template_name = 'judge/test_edit.html'
    title = 'Add a test'

    def get_context(self, problem, form  = TestNewForm()):
        return {
            'form' : form,
            'problem': problem,
            'problem_pk': problem.pk,
            'title' : self.title
        }
    
    def get(self, request, problem_id):
        problem = get_object_or_404(Problem, pk = problem_id)

        context = self.get_context(problem)
        return render(request, self.template_name, context)

    def add_single_test(self, form, problem, request):
        test = form.save(commit = False)
        test.stdin = request.FILES['stdinFile'].read()
        test.stdout = request.FILES['stdoutFile'].read()
        test.problem = problem
        test.save()

        problem.update_max_score()

        return True

    def add_zip_tests(self, form, problem, request):
        zipName = settings.BASE_DIR + '/tests.zip'

        with open(zipName, 'wb+') as zipFile:
            for chunk in request.FILES['zipFile'].chunks():
                zipFile.write(chunk)

        try:
            with ZipFile(zipName) as testsZip:
                fileNames = testsZip.namelist()
                fileNamesSet = set(fileNames)

                testCount = 0
                for inFileName in fileNames:
                    if not inFileName.endswith('.in'):
                        continue

                    testName = inFileName[:-3]
                    if testName + '.sol' in fileNamesSet:
                        outFileName = testName + '.sol'
                    elif testName + '.out' in fileNamesSet:
                        outFileName = testName + '.out'
                    else:
                        continue

                    testCount += 1

                    test = Test(problem = problem)
                    test.time_limit = form.cleaned_data['time_limit']
                    test.mem_limit  = form.cleaned_data['mem_limit']
                    test.score      = form.cleaned_data['score']

                    with testsZip.open(inFileName, 'r') as inFile:
                        test.stdin = inFile.read()
                    with testsZip.open(outFileName, 'r') as outFile:
                        test.stdout = outFile.read()

                    test.save()

            os.remove(zipName)

            if testCount:
                problem.update_max_score()

                messageText = '{0} tests were added'.format(testCount)
                messages.add_message(request, messages.SUCCESS, messageText)
            else:
                messageText = 'No test were added'
                messages.add_message(request, messages.WARNING, messageText)

        except BadZipFile:
            form.add_error('zipFile', 'Invalid zip file')
            return False

        return True

    def post(self, request, problem_id):
        problem = get_object_or_404(Problem, pk = problem_id)
        form = TestNewForm(request.POST, request.FILES)

        success = False
        if form.is_valid():
            if form.cleaned_data['zipFile']:
                success = self.add_zip_tests(form, problem, request)
            else:
                success = self.add_single_test(form, problem, request)

        if success:
            return redirect('judge:test_list', problem_id = problem_id)
        else:
            context = self.get_context(problem, form)
            return render(request, self.template_name, context)

class TestEdit(View):
    template_name = 'judge/test_edit.html'
    title = 'Edit test'

    def get_context(self, form, test):
        return {
            'form' : form,
            'problem': test.problem,
            'title': self.title,
            'pk': test.pk,
            'problem_pk': test.problem.pk
        }

    def get(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        form = TestEditForm(instance = test)

        context = self.get_context(form, test)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        form = TestEditForm(request.POST, request.FILES, instance = test)
        problem = test.problem

        if not form.is_valid(update = True):
            context = self.get_context(form, test)
            return render(request, self.template_name, context)

        test = form.save(commit = False)

        if not form.cleaned_data['stdinFile'] == None:
            test.stdin = request.FILES['stdinFile'].read()
        if not form.cleaned_data['stdoutFile'] == None:
            test.stdout = request.FILES['stdoutFile'].read()

        test.problem = problem
        test.save()

        problem.update_max_score()

        return redirect('judge:test_list', problem_id = problem.pk)

class TestDelete(View):
    template_name = 'judge/test_delete.html'

    def get_tests(self, ids):
        idList = ids.split(',')
        tests = Test.objects.filter(id__in = idList)

        if tests:
            return Test.objects.filter(id__in = idList)
        else:
            raise Http404

    def get(self, request, ids):
        tests = self.get_tests(ids)

        context = {
            'problem_pk': tests[0].problem.pk,
            'test_count': tests.count()
        }

        return render(request, self.template_name, context)

    def post(self, request, ids):
        tests = self.get_tests(ids)
        problem = tests[0].problem
        tests.delete()

        problem.update_max_score()

        messageText = 'You\'ve successfuly deleted the tests'
        messages.add_message(request, messages.SUCCESS, messageText)

        return redirect('judge:test_list', problem_id = problem.pk)

class ProblemGlobalForm(forms.Form):
    timeLimit = forms.DecimalField(required = False, decimal_places = 4,
                                        label = 'Time limit (sec)')
    memoryLimit = forms.IntegerField(required = False, 
                                        label = 'Memory limit (MB)')
    testScore = forms.DecimalField(required = False, decimal_places = 4,
                                        label = 'Points per test')

class TestList(View):
    template_name = 'judge/test_list.html'
    checkboxPrefix = 'test_sel_'

    def get_context(self, problem_id, form = ProblemGlobalForm()):
        problem = get_object_or_404(Problem, pk = problem_id)
        tests = problem.test_set.all();

        groupedTests = {}

        for test in tests:
            if test.test_group in groupedTests:
                groupedTests[test.test_group].append(test)
            else:
                groupedTests[test.test_group] = [test]

        testGroups = problem.testgroup_set.all()

        for group in testGroups:
            if not group in groupedTests:
                groupedTests[group] = []

        return {
            'tests_by_group' : groupedTests,
            'problem_pk': problem_id,
            'form': form,
            'checkboxPrefix': self.checkboxPrefix
        }
    
    def get(self, request, problem_id):
        context = self.get_context(problem_id)
        return render(request, self.template_name, context)

    def update_tests(self, request, problem_id):
        form = ProblemGlobalForm(request.POST)

        if not form.is_valid():
            context = self.get_context(problem_id, form = form)
            return render(request, self.template_name, context)

        timeLimit = form.cleaned_data['timeLimit']
        memoryLimit = form.cleaned_data['memoryLimit']
        testScore = form.cleaned_data['testScore']

        testIds = request.POST.getlist('test-select')
        problem = get_object_or_404(Problem, pk = problem_id)

        for pk in testIds:
            test = get_object_or_404(Test, pk = pk)

            if timeLimit != None:
                test.time_limit = timeLimit
            if memoryLimit != None:
                test.mem_limit = memoryLimit
            if testScore != None:
                test.score = testScore

            test.save()
        
        problem.update_max_score()

        if not testIds:
            messageText = 'No tests selected for update'
            messages.add_message(request, messages.WARNING, messageText)
        elif (not timeLimit) and (not memoryLimit) and (not testScore):
            messageText = 'No fields selected for update'
            messages.add_message(request, messages.WARNING, messageText)
        else:
            messageText = '{0} tests updated successfully'.format(len(testIds))
            messages.add_message(request, messages.SUCCESS, messageText)

        context = self.get_context(problem_id)
        return render(request, self.template_name, context)

    def delete_tests(self, request, problem_id):
        testIds = request.POST.getlist('test-select')
        testStr = ','.join(testIds)

        if not testStr:
            messageText = 'No tests selected for deletion'
            messages.add_message(request, messages.WARNING, messageText)

            return redirect('judge:test_list', problem_id = problem_id)
        else:
            return redirect('judge:test_delete', ids = testStr)

    def post(self, request, problem_id):
        if 'update' in request.POST:
            return self.update_tests(request, problem_id)
        elif 'delete' in request.POST:
            return self.delete_tests(request, problem_id)
        
class TestInput(View):
    def get(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        return HttpResponse(test.stdin, content_type = 'text/plain')

class TestOutput(View):
    def get(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        return HttpResponse(test.stdout, content_type = 'text/plain')
