import io
import os
import subprocess

from zipfile import ZipFile, BadZipFile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import InvalidPage, Paginator
from django.core.serializers import serialize, deserialize
from django.core.urlresolvers import reverse
from django.db.transaction import set_autocommit, commit
from django import forms
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView, View

from media_manager.models import MediaFile

from judge.models import Problem, Test, Solution, UserProblemData
from judge.tasks import test_solution, retest_problem, compile_program

class ProblemList(TemplateView):
    template_name = 'judge/problem_list.html'

    def get_context_data(self, page = 1, tags = ''):
        context = super(ProblemList, self).get_context_data()

        problems = Problem.objects.defer('statement')
        if not self.request.user.has_perm('judge.see_hidden_problems'):
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

        paginator = Paginator(problems, 14)

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
                
                    if solData.max_score == prob.max_score:
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
            return redirect(reverse('judge:problem_list'))
        else:
            return redirect(reverse('judge:problem_list_tags', 
                args=(tagsStr,)))

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
        exclude = ['max_score', 'visible', 'custom_checker', 'custom_grader', 
                'grader_header_filename', 'grader_header', 'grader_source']

class ProblemNew(PermissionRequiredMixin, View):
    permission_required = 'judge.add_problem'
    template_name = 'judge/problem_edit.html'

    def get(self, request):
        problem = Problem.objects.create()

        return redirect(reverse('judge:problem_edit', args=(problem.pk,)))

class ProblemEdit(PermissionRequiredMixin, View):
    permission_required = 'judge.add_problem'
    template_name = 'judge/problem_edit.html'

    def get_context(self, problem, form):
        return {
            'form' : form,
            'curTags': problem.tags.names(),
            'problem': problem
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
        return redirect(reverse('judge:problem_details', args = (pk,)))

class ProblemDelete(PermissionRequiredMixin, View):
    permission_required = 'judge.delete_problem'
    template_name = 'judge/problem_delete.html'

    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)

        context = {
            'modelName': problem.title,
            'modelType': 'problem',
            'cancelUrl': reverse('judge:problem_edit', args = (pk,)),
            'problem': problem
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        curProblem = Problem.objects.get(pk = pk)
        curProblem.delete()

        messageText = 'You\'ve Successfuly deleted this problem'
        messages.add_message(request, messages.SUCCESS, messageText)
        
        return redirect(reverse('judge:problem_list'))

class ProblemMedia(PermissionRequiredMixin, TemplateView):
    permission_required = 'judge.add_media_to_problem'
    template_name = 'judge/problem_media.html'

    def get_context_data(self, **kwargs):
        context = super(ProblemMedia, self).get_context_data(**kwargs)

        context['problem'] = get_object_or_404(Problem, pk = kwargs['pk'])
        return context

class ProblemCheckerForm(forms.Form):
    useCustomChecker = forms.BooleanField(label = 'Use custom checker', 
                    required = False)
    customChecker = forms.FileField(required = False, 
                    label = 'Checker source (c++) / binary (if used)')

    def is_valid(self, has_checker = False):
        valid = super(ProblemCheckerForm, self).is_valid()

        data = self.cleaned_data
        if has_checker:
            return valid
        elif data.get('useCustomChecker') and (not data.get('customChecker')):
            self.add_error('customChecker', 'Provide a checker')
            valid = False

        return valid

class ProblemGraderForm(forms.Form):
    useCustomGrader = forms.BooleanField(label = 'Use custom grader', 
                    required = False)
    graderHeaderFilename = forms.CharField(label = 'The name of the header file'
                    + ' to be included in the solutions',
                    required = False)
    graderHeader = forms.FileField(label = 'Grader header file (.h)',
                    required = False)
    graderSource = forms.FileField(label = 'Grader source file (.cpp)',
                    required = False)
                    
    def is_valid(self, has_grader = False):
        valid = super(ProblemGraderForm, self).is_valid()
        data = self.cleaned_data

        if data.get('useCustomGrader'):
            if not data.get('graderHeaderFilename'):
                self.add_error('graderHeaderFilename', 
                        'Provide a grader header filename')
                valid = False
            elif not data.get('graderHeaderFilename').endswith('.h'):
                self.add_error('graderHeaderFilename',
                        'The grader header filename must end with ".h"')
                valid = False

        if data.get('useCustomGrader') and (not has_grader):
            if not data.get('graderHeader'):
                self.add_error('graderHeader', 'Provide a grader header')
                valid = False

            if not data.get('graderSource'):
                self.add_error('graderSource', 'Provide a grader source')
                valid = False

        return valid

class ProblemGrading(PermissionRequiredMixin, View):
    permission_required = 'judge.add_checker_to_problem'
    template_name = 'judge/problem_grading.html'

    def get_context(self, pk, checkerForm = None, graderForm = None):
        problem = get_object_or_404(Problem, pk = pk)

        if not checkerForm:
            checkerForm = ProblemCheckerForm()

            checkerForm.fields['useCustomChecker'].initial = \
                    problem.custom_checker
        if not graderForm:
            graderForm = ProblemGraderForm()
            graderForm.fields['useCustomGrader'].initial = problem.custom_grader
            graderForm.fields['graderHeaderFilename'].initial = \
                    problem.grader_header_filename


        return {
            'checkerForm': checkerForm,
            'graderForm': graderForm,
            'problem': problem
        }

    def get(self, request, pk):
        context = self.get_context(pk)
        return render(request, self.template_name, context)

    def update_checker(self, request, pk):
        form = ProblemCheckerForm(request.POST, request.FILES)
        problem = get_object_or_404(Problem, pk = pk)

        if not form.is_valid(has_checker = problem.custom_checker):
            context = self.get_context(pk, checkerForm = form)
            return render(request, self.template_name, context)

        problem.custom_checker = form.cleaned_data.get('useCustomChecker')

        if problem.custom_checker:
            name = form.cleaned_data.get('customChecker').name
            grader = os.path.join(settings.BASE_DIR, 'judge/graders',
                    str(problem.pk))

            if name.endswith('.cpp'):
                with open(grader + '.cpp', 'wb') as dest:
                    dest.write(request.FILES['customChecker'].read())

                try:
                    compile_program(grader + '.cpp', grader)
                    messages.success(request, 'Checker successfully compiled')
                    problem.save()
                except subprocess.CalledProcessError:
                    messages.error(request, 'Compilation error (syntax)')
                except subprocess.TimeoutExpired:
                    messages.error(request, 'Compilation error (timeout)')
            elif name:
                with open(grader, 'wb') as dest:
                    dest.write(request.FILES['customChecker'].read())

                problem.save()
                messages.success(request, 'Checker successfully uploaded')
        else:
            problem.save()
            messages.success(request, 'Checker removed successfully')

        return self.get(request, pk)

    def update_grader(self, request, pk):
        form = ProblemGraderForm(request.POST, request.FILES)
        problem = get_object_or_404(Problem, pk = pk)

        if not form.is_valid(has_grader = problem.custom_grader):
            context = self.get_context(pk, graderForm = form)
            return render(request, self.template_name, context)

        data = form.cleaned_data

        problem.custom_grader = data.get('useCustomGrader')
        #print(problem.custom_grader)

        if data.get('useCustomGrader'):
            problem.grader_header_filename = data.get('graderHeaderFilename')
            if data['graderHeader']:
                problem.grader_header = request.FILES['graderHeader'].read()
            if data['graderSource']:
                problem.grader_source = request.FILES['graderSource'].read()
        else:
            problem.grader_header_filename = ''
            problem.grader_header = ''
            problem.grader_source = ''

        problem.save()
        messages.success(request, 'Grader updated successfully')

        return self.get(request, pk)

    def post(self, request, pk):
        if 'checker' in request.POST:
            return self.update_checker(request, pk)
        elif 'grader' in request.POST:
            return self.update_grader(request, pk)
        else:
            return self.get(request, pk)

class ProblemRetest(PermissionRequiredMixin, View):
    permission_required = 'judge.retest_problem'
    template_name = 'judge/problem_retest.html'

    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)
        solCnt = Solution.objects.filter(problem = problem).count()

        context = {
            'problem': problem,
            'solutionCount': solCnt
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)

        retest_problem(problem).delay()

        messageText = "Solutions added to the queue."
        messages.add_message(request, messages.SUCCESS, messageText)

        return redirect(reverse('judge:problem_edit', args=(pk,)))

class ProblemVisibility(PermissionRequiredMixin, View):
    permission_required = 'judge.change_visibility_of_problem'
    template_name = 'judge/problem_visibility.html'

    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)

        context = { 
            'visible': problem.visible,
            'problem': problem
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        prob = get_object_or_404(Problem, pk = pk)
        prob.visible = not prob.visible
        prob.save()

        visText = 'visible' if prob.visible else 'hidden'
        messageText = 'Visibility is successfully changed to ' + visText
        messages.add_message(request, messages.SUCCESS, messageText)

        return redirect(reverse('judge:problem_edit', args=(prob.pk,)))

class ProblemImportForm(forms.Form):
    import_data = forms.FileField()

class PorblemImport(PermissionRequiredMixin, View):
    permission_required = 'judge.import_problem'
    template_name = 'judge/problem_import.html'

    def get_response(self, request, form = ProblemImportForm()):
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def get(self, request):
        return self.get_response(request = request)
    
    def import_problem(self, curZip):
        problem_map = {}
        problems = {}
        with curZip.open('problem.json') as f:
            for p in deserialize('json', f.read()):
                old_pk = p.object.pk

                p.object.pk = None
                p.save()

                problem_map[old_pk] = p.object.pk
                problems[p.object.pk] = p.object

        test_group_map = {None: None}
        with curZip.open('test_group.json') as f:
            for tg in deserialize('json', f.read()):
                old_pk = tg.object.pk
                tg.object.pk = None
                tg.object.visible = False
                tg.object.problem_id = problem_map[tg.object.problem_id]

                tg.save()

                test_group_map[old_pk] = tg.object.pk

        with curZip.open('test.json') as f:
            for t in deserialize('json', f.read()):
                t.object.pk = None

                t.object.problem_id = problem_map[t.object.problem_id]
                t.object.test_group_id = test_group_map[
                    t.object.test_group_id]
                
                t.save()

        with curZip.open('media.json') as f:
            for m in deserialize('json', f.read()):
                m.object.pk = None

                problem_pk = problem_map[m.object.object_id]
                m.object.content_object = problems[problem_pk]

                if not os.path.isfile(m.object.media.url[1:]):
                    curZip.extract(m.object.media.url[1:])

                m.save()

    def post(self, request):
        form = ProblemImportForm(request.POST, request.FILES)

        if not form.is_valid():
            return self.get_response(request, form = form)

        s = io.BytesIO()
        for chunk in request.FILES['import_data'].chunks():
            s.write(chunk)

        try:
            with ZipFile(s, 'r') as curZip:
                self.import_problem(curZip)
        except (BadZipFile, KeyError):
            form.add_error('import_data', 'Invalid file')
            return self.get_response(request, form = form)
        else:
            messages.success(request, 'Problem(s) imported successfully')
            return redirect(reverse('judge:problem_list'))
            
class ProblemExport(PermissionRequiredMixin, View):
    permission_required = 'judge.change_problem'
    
    def get(self, request, pk):
        problem = get_object_or_404(Problem, pk = pk)

        s = io.BytesIO()
        with ZipFile(s, 'w') as curZip:
            curZip.writestr('problem.json', serialize('json', [problem]))
            curZip.writestr('test_group.json', serialize('json',
                problem.testgroup_set.all()))
            curZip.writestr('test.json', serialize('json',
                problem.test_set.all()))

            media = MediaFile.get_for_object(problem).all()
            for f in media:
                try:
                    curZip.write(f.media.url[1:])
                except FileNotFoundError:
                    f.delete()

            curZip.writestr('media.json', serialize('json', media))

        response = HttpResponse(s.getvalue(), content_type = \
            'application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="problem.zip"'
        return response
