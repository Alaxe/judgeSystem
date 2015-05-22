from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, View

from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.forms import ModelForm

from judge.models import Problem, Test

class ProblemForm(ModelForm):
    class Meta:
        model = Problem
        fields = '__all__'

class ProblemList(TemplateView):
    template_name = 'judge/problem_list.html'

    def get_context_data(self, page_id = 1):
        problems_per_page = 3

        context = super(ProblemList, self).get_context_data()
        page_id = int(page_id)

        if page_id < 1 :
            raise Http404('Page index start from 1')

        start_ind = (page_id - 1) * problems_per_page
        end_ind = start_ind + problems_per_page

        problems = Problem.objects.all()[start_ind:end_ind]

        if not problems:
            raise Http404('Page not found')
        
        context['problem_list'] = problems

        return context

class ProblemDetails(DetailView):
    model = Problem
    context_object_name = 'problem'
    template_name = 'judge/problem_details.html'

class ProblemNew(View):
    template_name = 'judge/edit_problem.html'
    title = 'Add Problem'

    def get_context(self, form):
        return {
            'form' : form,
            'title' : self.title}

    def get(self, request):
        context = self.get_context(ProblemForm())
        return render(request, self.template_name, context)

    def post(self, request):
        form = ProblemForm(request.POST)

        if not form.is_valid():
            context = self.get_context(form)
            return render(request, self.template_name, context)

        problem = form.save()
        url = reverse('judge:problem_details', args = (problem.pk,))
        return HttpResponseRedirect(url)

class ProblemEdit(View):
    template_name = 'judge/edit_problem.html'
    title = 'Edit Problem'

    def get_context(self, problem, form):
        pk = problem.pk
        return {
            'form' : form,
            'title': self.title,
            'tests': problem.test_set,
            'pk'   : pk}

    def get(self, request, pk = 0):
        problem = get_object_or_404(Problem, pk = pk)
        tests = problem.test_set
        form = ProblemForm(instance = problem)

        context = self.get_context(problem, form)
        return render(request, self.template_name, context)

    def post(self, request, pk = 0):
        problem = get_object_or_404(Problem, pk = pk)

        form = ProblemForm(request.POST, instance = problem)

        if not form.is_valid():
            context = self.get_context(problem, form)
            return render(request, self.template_name, context)

        form.save()
        url = reverse('judge:problem_details', args = (pk,))
        return HttpResponseRedirect(url)


