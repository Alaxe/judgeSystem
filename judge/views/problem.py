from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.db.transaction import set_autocommit, commit
from django.forms import ModelForm, Form, IntegerField, DecimalField
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView, View

from tags.utils import tags_by_category, filter_by_tags
from tags.models import TagInstance, Tag

from judge.models import Problem, Test, Solution, UserProblemData
from judge.tasks import test_solution, retest_problem

def list_tag_inst(pk):
        content_type = ContentType.objects.get_for_model(Problem)
        curInst = TagInstance.objects.filter(object_id = pk,
                                            content_type = content_type)
        return curInst

class ProblemForm(ModelForm):
    class Meta:
        model = Problem
        exclude = ['maxScore', 'visible']

class ProblemList(TemplateView):
    template_name = 'judge/problem_list.html'

    def get_context_data(self, page = 1):
        curTagsLabels = self.request.GET.getlist('tags')
        curTags = Tag.objects.filter(label__in = curTagsLabels)

        problems = Problem.objects.filter(visible = True)
        problems = filter_by_tags(problems, curTags)

        problems.sort(key=lambda x: x.id, reverse = True)
        

        paginator = Paginator(problems, 20)
        context = super(ProblemList, self).get_context_data()

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
                
                prob.tagInst = list_tag_inst(prob.pk)
        
        context['page'] = page
        
        allTags = tags_by_category()
        curTagsSet = set(curTagsLabels)

        for cat in allTags:
            for tag in cat[1]:
                if tag.label in curTagsSet:
                    tag.active = True;
                
        context['tags'] = allTags;
        context['curTags'] = curTagsLabels;
    
        return context

class ProblemDetails(View):
    model = Problem
    context_object_name = 'problem'
    template_name = 'judge/problem_details.html'

    def get(self, request, pk):
        if not request.user.has_perm('judge.change_problem'):
            problem = get_object_or_404(Problem, pk = pk, visible = True)
        else:
            problem = get_object_or_404(Problem, pk = pk)
        solutions = []
        
        if request.user.is_authenticated():
            solutions = Solution.objects.filter(user = request.user,
                    problem = problem)[:20]

        context = {'problem': problem, 'solutions': solutions}
        return render(request, self.template_name, context)

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

class ProblemGlobalForm(Form):
    timeLimit = DecimalField(required = False, decimal_places = 4)
    memoryLimit = IntegerField(required = False)
    testScore = IntegerField(required = False)

class ProblemGlobal(View):
    template_name = 'judge/problem_global.html'

    def get_context(self, form, pk):
        return {
            'form': form,
            'problem_pk': pk
        }

    def get(self, request, pk):
        form = ProblemGlobalForm()
        context = self.get_context(form, pk)
        return render(request, self.template_name, context)
        
    def post(self, request, pk):
        form = ProblemGlobalForm(request.POST)

        if not form.is_valid():
            context = self.get_context(form, pk)
            return render(request, self.template_name, context)

        problem = get_object_or_404(Problem, pk = pk)

        timeLimit = form.cleaned_data['timeLimit']
        memoryLimit = form.cleaned_data['memoryLimit']
        testScore = form.cleaned_data['testScore']

        for test in problem.test_set.all():
            if timeLimit != None:
                test.time_limit = timeLimit
            if memoryLimit != None:
                test.mem_limit = memoryLimit
            if testScore != None:
                test.score = testScore

            test.save()
        
        if testScore != None:
            problem.maxScore = problem.test_set.count() * testScore
            problem.save()


        messageText = 'Test updated successfully'
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

class ProblemTags(View):
    template_name = 'judge/problem_tags.html'
    
    def get_response(self, request, pk,  curInst = []):
        allTags = tags_by_category()
        curLabels = { inst.tag.label for inst in curInst }
        context = {
            'problem_pk': pk,
            'tags': allTags,
            'curTags': curLabels
        }
        return render(request, self.template_name, context)

    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)
        curInst = list_tag_inst(pk)
        return self.get_response(request, pk, curInst = curInst)

    def post(self, request, pk):
        newTagLabels = request.POST.getlist('tags')
        newTags = Tag.objects.filter(label__in = newTagLabels)

        list_tag_inst(pk).delete()
        
        newTagInst = []
        for tag in newTags:
            content_type = ContentType.objects.get_for_model(Problem)
            tagInst = TagInstance(tag = tag, object_id = pk, 
                                    content_type = content_type)
            newTagInst.append(tagInst)
        
        TagInstance.objects.bulk_create(newTagInst)
        
        return self.get_response(request, pk, curInst = newTagInst)



