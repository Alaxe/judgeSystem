from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django import forms
from django.http import Http404, HttpResponse, HttpResponseRedirect,\
            HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from judge.models import Problem, Test

class TestForm(forms.ModelForm):
    stdinFile = forms.FileField(required=False)
    stdoutFile = forms.FileField(required=False)

    class Meta:
        model = Test
        exclude = ['stdin', 'stdout', 'problem']

    def is_valid(self, update=False):
        valid = super(TestForm, self).is_valid()
        
        if update:
            return valid

        if self.cleaned_data['stdinFile'] == None:
            self.add_error('stdinFile', 'Include input File')
            valid = False

        if self.cleaned_data['stdoutFile'] == None:
            self.add_error('stdoutFile', 'Include output file')
            valid = False

        return valid

class TestNew(View):
    template_name = 'judge/test_edit.html'
    title = 'Add a test'

    def get_context(self, form, problem):
        return {
            'form' : form,
            'problem': problem,
            'problem_pk': problem.pk,
            'title' : self.title
        }
    
    def get(self, request, problem_id):
        problem = get_object_or_404(Problem, pk = problem_id)

        context = self.get_context(TestForm(), problem)
        return render(request, self.template_name, context)

    def post(self, request, problem_id):
        problem = get_object_or_404(Problem, pk = problem_id)
        form = TestForm(request.POST, request.FILES)

        if not form.is_valid():
            context = self.get_context(form, problem)
            return render(request, self.template_name, context)

        test = form.save(commit = False)
        test.stdin = request.FILES['stdinFile'].read()
        test.stdout = request.FILES['stdoutFile'].read()
        test.problem = problem
        test.save()

        url = reverse('judge:problem_edit', args = (problem.pk,))
        return HttpResponseRedirect(url)

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
        form = TestForm(instance = test)

        context = self.get_context(form, test)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        form = TestForm(request.POST, request.FILES, instance = test)
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

        url = reverse('judge:test_list', args = (problem.pk,))
        return HttpResponseRedirect(url)

class TestDelete(View):
    template_name = 'judge/test_delete.html'

    def get(self, request, pk):
        test = get_object_or_404(Test, pk = pk)

        context = {
            'problem_pk': test.problem.pk
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        test.delete()

        messageText = 'You\'ve successfuly deleted this test'
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('judge:problem_edit', args=(test.problem.pk,))
        return HttpResponseRedirect(url)

class ProblemGlobalForm(forms.Form):
    timeLimit = forms.DecimalField(required = False, decimal_places = 4)
    memoryLimit = forms.IntegerField(required = False)
    testScore = forms.IntegerField(required = False)

class TestList(View):
    template_name = 'judge/test_list.html'
    checkboxPrefix = 'test_sel_'

    def get_context(self, pk, form = ProblemGlobalForm()):
        problem = get_object_or_404(Problem, pk = pk)
        tests = problem.test_set.all();

        return {
            'problem' : problem,
            'tests' : tests,
            'problem_pk': pk,
            'form': form,
            'checkboxPrefix': self.checkboxPrefix
        }
    
    def get(self, request, pk):
        context = self.get_context(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = ProblemGlobalForm(request.POST)
        context = self.get_context(pk, form = form)

        if not form.is_valid():
            return render(request, self.template_name, context)

        timeLimit = form.cleaned_data['timeLimit']
        memoryLimit = form.cleaned_data['memoryLimit']
        testScore = form.cleaned_data['testScore']

        testIds = request.POST.getlist('test-select')
        problem = get_object_or_404(Problem, pk = pk)

        for curPk in testIds:
            test = get_object_or_404(Test, pk = curPk)

            if timeLimit != None:
                test.time_limit = timeLimit
            if memoryLimit != None:
                test.mem_limit = memoryLimit
            if testScore != None:
                problem.maxScore -= test.score
                problem.maxScore += testScore

                test.score = testScore

            test.save()
        
        print('hi')
        problem.save()

        return render(request, self.template_name, context)

class TestInput(View):
    def get(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        return HttpResponse(test.stdin, content_type = 'text/plain')

class TestOutput(View):
    def get(self, request, pk):
        test = get_object_or_404(Test, pk = pk)
        return HttpResponse(test.stdout, content_type = 'text/plain')
