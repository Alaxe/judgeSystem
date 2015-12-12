from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.forms import ModelForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView

from judge.models import TestGroup, Problem, Test

class TestGroupForm(ModelForm):
    class Meta:
        model = TestGroup
        exclude = ['problem']

class TestGroupEdit(View):
    temlpate_name = 'judge/test_group_edit.html'
    title = 'Edit Test group'
    redir_pattern = 'judge:test_list'

    def get_context(self, **kwargs):
        context = {'title': self.title }

        if 'pk' in kwargs:
            context['test_group'] = get_object_or_404(TestGroup, pk = kwargs['pk'])
            context['problem_pk'] = context['test_group'].problem.pk
        else:
            context['problem_pk'] = kwargs['problem_id']

        problem = get_object_or_404(Problem, pk = context['problem_pk'])

        if 'form' in kwargs:
            context['form'] = kwargs['form']
        elif 'test_group' in context:
            context['form'] = TestGroupForm(instance = context['test_group'])
        else:
            context['form'] = TestGroupForm()

        tests_Q = Q(test_group__isnull = True)
        if 'test_group' in context:
            tests_Q |= Q(test_group = context['test_group'])
            context['selected'] = context['test_group'].test_set.all()

        context['tests'] = problem.test_set.filter(tests_Q)

        return context

    def get(self, request, **kwargs):
        return render(request, self.temlpate_name, self.get_context(**kwargs))

    def update_tests(self, testGroup, request):
        for test in testGroup.test_set.all():
            test.test_group = None
            test.save()

        testPk = request.POST.getlist('test-select')
        for test in Test.objects.filter(pk__in = testPk):
            test.test_group = testGroup
            test.save()

    def post(self, request, pk):
        testGroup = get_object_or_404(TestGroup, pk = pk)
        form = TestGroupForm(request.POST, instance = testGroup)

        if form.is_valid():
            testGroup = form.save()

            self.update_tests(testGroup, request)
            testGroup.problem.update_max_score()

            return redirect(self.redir_pattern, problem_id = testGroup.problem.pk)
        else:
            context = self.get_context(form = form, pk = pk)
            return render(request, self.template_name, context)

class TestGroupNew(TestGroupEdit):
    title = 'New Test group'

    def post(self, request, problem_id):
        form = TestGroupForm(request.POST)

        if form.is_valid():
            testGroup = form.save(commit = False)
            testGroup.problem = get_object_or_404(Problem, pk = problem_id)
            testGroup.save()

            self.update_tests(testGroup, request)
            testGroup.problem.update_max_score()
            
            return redirect(self.redir_pattern, problem_id = problem_id)
        else:
            context = self.get_context(form = form, problem_id = problem_id)
            return render(request, self.template_name, context)

class TestGroupDelete(View):
    template_name = 'judge/test_group_delete.html'

    def get(self, request, pk):
        testGroup = get_object_or_404(TestGroup, pk = pk)
        context = {
            'test_group': testGroup,
            'problem_pk': testGroup.problem.pk
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        testGroup = get_object_or_404(TestGroup, pk = pk)
        testGroup.delete()
        testGroup.problem.update_max_score()

        messages.success(request, 'Test group deleted successfully')
        return redirect('judge:test_list', problem_id = testGroup.problem.pk)
