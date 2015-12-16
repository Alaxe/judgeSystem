import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import Form, CharField, Textarea
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect,\
        HttpResponseForbidden
from django.views.generic import DetailView, View
from django.utils import timezone

from judge.models import *
from judge.tasks import test_solution

def may_view_solution(user, solution):
    if user.has_perm('judge.view_foreign_solution'):
        return True
    else:
        return solution.user == user

class SolutionDetails(View):
    template_name = 'judge/solution_details.html'

    def get(self, request, pk):
        sol = get_object_or_404(Solution, pk = pk)
        
        if may_view_solution(request.user, sol):
            context = { 
                'solution': sol,
                'results_by_group': sol.get_results_by_group(),
                'pk': sol.pk,
            }
            return render(request, self.template_name, context)
        else:
            url = reverse('judge:problem_list')
            return HttpResponseRedirect(url)

class SolutionSubmitForm(Form):
    source = CharField(label = 'Source Code',
                            widget = Textarea())

class SolutionSubmit(View):
    template_name = 'judge/solution_submit.html'
            
    def render(self, request):
        context = {
            'problem': self.problem,
            'form': self.form,}
        return render(request, self.template_name, context)

    def get(self, request, pk):
        self.form = SolutionSubmitForm()
        if request.user.has_perm('judge.problem_hidden'):
            self.problem = get_object_or_404(Problem, pk = pk)
        else:
            self.problem = get_object_or_404(Problem, pk = pk, visible = True)

        if not request.user.is_active:
            return HttpResponseRedirect(reverse('judge:login'))

        return self.render(request)

    def post(self, request, pk):
        self.problem = get_object_or_404(Problem, pk = pk)
        self.form = SolutionSubmitForm(request.POST)
        
        user = request.user
        if not user.is_active:
            return HttpResponseRedirect(reverse('judge:login'))

        if not self.form.is_valid():
            return self.render(request)

        try:
            data = UserProblemData.objects.get(user = user,
                                                problem = self.problem)

            nextSubmit = data.last_submit + datetime.timedelta(seconds = 27)

            if nextSubmit > timezone.now():
                messageText = 'You can submit a solution once every 30 \
                        seconds. Try again in a little bit.'
                messages.add_message(request, messages.WARNING, messageText)
                return self.render(request)

            else:
                data.last_submit = timezone.now()
                data.save()

        except UserProblemData.DoesNotExist:
            data = UserProblemData(user = user,
                                    problem = self.problem,
                                    last_submit = timezone.now())

            data.save()
            UserStatts.get_for_user(user).update_statts()

        source = self.form.cleaned_data['source']
        solution = Solution(
            source = source,
            submit_date = timezone.now(),
            grader_message = 'In Queue',
            user = user,
            problem = self.problem)

        solution.save()
        
        test_solution.delay(solution)

        url = reverse('judge:solution_details', args = (solution.pk,))
        return HttpResponseRedirect(url)

class SolutionSource(View):
    def get(self, request, pk):
        sol = get_object_or_404(Solution, pk = pk)

        if may_view_solution(request.user, sol):
            return HttpResponse(sol.source, content_type = 'text/plain')
        else:
            return HttpResponseForbidden()
