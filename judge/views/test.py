from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ModelForm, FileField
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from judge.models import Problem, Test

class TestForm(ModelForm):
    stdinFile = FileField(required=False)
    stdoutFile = FileField(required=False)

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
    title = 'Add Test'

    def get_context(self, form, problem):
        return {
            'form' : form,
            'problem': problem,
            'title' : self.title,
            'action': 'create'
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
    title = 'Edit Test'

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

class TestList(View):
    template_name = 'judge/test_list.html'
    
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)

        context = {
            'problem' : problem,
            'tests' : problem.test_set.all(),
            'problem_pk': pk
        }

        return render(request, self.template_name, context)
