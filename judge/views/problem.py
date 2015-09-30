from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.db.transaction import set_autocommit, commit
from django import forms
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView, View

from judge.models import Problem, Test, Solution, UserProblemData
from judge.tasks import test_solution, retest_problem

class ProblemList(TemplateView):
    template_name = 'judge/problem_list.html'

    def get_context_data(self, page = 1, tags = ''):
        context = super(ProblemList, self).get_context_data()

        problems = Problem.objects.all()
        if not self.request.user.has_perm('judge.problem_hidden'):
            problems = problems.filter(visible = True)

        context['curTags'] = []
        if tags != '':
            context['curTags'] = tags.split(',')

            for tag in context['curTags']:
                problems = problems.filter(tags__name__in = (tag,))

            context['paginate_name'] = 'judge:problem_list_tags_page'
            context['paginate_extra_kwargs'] = {'tags': tags }

        else:
            context['paginate_name'] = 'judge:problem_page'
            context['paginate_extra_kwargs'] = {}

        paginator = Paginator(problems, 10)

        try:
            page = paginator.page(page)
        except InvalidPage:
            raise Http404
        
        user = self.request.user

        if user.is_authenticated():
            for prob in page.object_list :
                
                try :
                    solData = UserProblemData.objects.get(problem = prob, 
                                                        user = user)
                
                    if solData.maxScore == prob.maxScore:
                        prob.status = 'solved'
                    else:
                        prob.status = 'attempted'

                except UserProblemData.DoesNotExist :
                    prob.status = 'not_attempted'
        
        context['page'] = page
    
        return context

class ProblemFilter(View):
    template_name = 'judge/problem_filter.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        selectedTags = request.POST.getlist('tag_select')

        tagsStr = ''
        for tag in selectedTags:
            if not tagsStr:
                tagsStr = tag
            else:
                tagsStr += ',' + tag



        if not tagsStr:
            url = reverse('judge:problem_list')
        else:
            url = reverse('judge:problem_list_tags', args=(tagsStr,))
        return HttpResponseRedirect(url)

class ProblemDetails(TemplateView):
    template_name = 'judge/problem_details.html'

    def get_context_data(self, pk):
        if not self.request.user.has_perm('judge.problem_hidden'):
            problem = get_object_or_404(Problem, pk = pk, visible = True)
        else:
            problem = get_object_or_404(Problem, pk = pk)
        solutions = []
        
        if self.request.user.is_authenticated():
            solutions = Solution.objects.filter(user = self.request.user,
                    problem = problem)[:20]

        return {'problem': problem, 'solutions': solutions}


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        exclude = ['maxScore', 'visible', 'customChecker']

class ProblemNew(View):
    template_name = 'judge/problem_edit.html'
    title = 'Add a problem'

    def get_context(self, form):
        return {
            'form' : form,
            'title' : self.title
        }

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
    template_name = 'judge/problem_edit.html'
    title = 'Edit statement'

    def get_context(self, problem, form):
        pk = problem.pk
        return {
            'form' : form,
            'title': self.title,
            'tests': problem.test_set,
            'problem_pk'   : pk
        }

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

class ProblemDelete(View):
    template_name = 'judge/problem_delete.html'

    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)

        context = {
            'modelName': problem.title,
            'modelType': 'problem',
            'cancelUrl': reverse('judge:problem_edit', args = (pk,)),
            'problem_pk': pk
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        curProblem = Problem.objects.get(pk = pk)
        curProblem.delete()

        messageText = 'You\'ve Successfuly deleted this problem'
        messages.add_message(request, messages.SUCCESS, messageText)
        
        url = reverse('judge:problem_list')
        return HttpResponseRedirect(url)

class ProblemCheckerForm(forms.Form):
    useCustomChecker = forms.BooleanField(label = 'Use custom checker', 
                    required = False)
    customChecker = forms.FileField(required = False, 
                    label = 'Upload checker (if used)')

    def is_valid(self):
        valid = super(ProblemCheckerForm, self).is_valid()

        data = self.cleaned_data
        if data.get('useCustomChecker') and (not data.get('customChecker')) :
                self.add_error('customChecker', 'You need to provide a checker')
                valid = False

        return valid

class ProblemChecker(View):
    template_name = 'judge/problem_checker.html'

    def get_context(self, pk, form = None):
        if not form:
            problem = get_object_or_404(Problem, pk = pk)
            form = ProblemCheckerForm()
            form.fields['useCustomChecker'].initial = problem.customChecker

        return {
            'form': form,
            'problem_pk': pk
        }

    def get(self, request, pk):
        context = self.get_context(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = ProblemCheckerForm(request.POST, request.FILES)
        problem = get_object_or_404(Problem, pk = pk)

        if not form.is_valid():
            context = self.get_context(pk, form = form)
            return render(request, self.template_name, context)

        problem.customChecker = form.cleaned_data.get('useCustomChecker')
        problem.save()

        if problem.customChecker:
            dest = open('judge/graders/' + str(problem.pk), 'wb')
            dest.write(request.FILES['customChecker'].read())
            dest.close()

        messageText = 'Checker successfully updated'
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('judge:problem_edit', args=(pk,))
        return HttpResponseRedirect(url)

class ProblemRetest(View):
    template_name = 'judge/problem_retest.html'

    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)
        solCnt = Solution.objects.filter(problem = problem).count()

        context = {
            'problem_pk': pk,
            'solutionCount': solCnt
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)

        retest_problem.delay(problem)

        messageText = "Solutions added to the queue."
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('judge:problem_edit', args=(pk,))
        return HttpResponseRedirect(url)

        problem = get_object_or_404(Problem, pk = pk)
        return HttpResponse(problem.stdin, content_type="text/plain")

class ProblemVisibility(View):
    template_name = 'judge/problem_visibility.html'

    def get(self, request, pk):
        prob = get_object_or_404(Problem, pk = pk)

        context = { 
            'visible': prob.visible,
            'problem_pk': prob.pk
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        prob = get_object_or_404(Problem, pk = pk)
        prob.visible = not prob.visible
        prob.save()

        visText = 'visible' if prob.visible else 'hidden'
        messageText = 'Visibility is successfully changed to ' + visText
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('judge:problem_edit', args=(prob.pk,))
        return HttpResponseRedirect(url)
