from django import template
from django.core.urlresolvers import reverse

from judge.models import Solution, TestResult

register = template.Library()

@register.inclusion_tag('judge/problem_edit_nav.html', takes_context = True)
def problem_edit_nav(context, *args, **kwargs):
    page = kwargs.get('page', '')
    problem_pk = context['problem_pk']

    return {
        'curPage': page,
        'pages': [ {
            'name': 'statement',
            'url': reverse('judge:problem_edit', args = (problem_pk,)),
            'text': 'Edit statement'
        }, {
            'name': 'tests',
            'url': reverse('judge:test_list', args = (problem_pk,)),
            'text': 'Edit tests'
        }, {
            'name': 'global',
            'url': reverse('judge:problem_global', args = (problem_pk,)),
            'text': 'Change global settings'
        }, {
            'name': 'retest',
            'url': reverse('judge:problem_retest', args = (problem_pk,)),
            'text': 'Retest problem'
        }, {
            'name': 'visibility',
            'url': reverse('judge:problem_visibility', args= (problem_pk,)),
            'text': 'Change visibility'
        }, {
            'name': 'tags',
            'url': reverse('judge:problem_tags', args = (problem_pk,)),
            'text': 'Edit tags'
        },{
            'name': 'delete',
            'url': reverse('judge:problem_delete', args = (problem_pk,)),
            'text': 'Delete problem'
        }
     ]
    }

@register.filter
def status_class(obj, *args, **kwargs):
    maxScore = 1000
    if type(obj) is Solution:
        if obj.grader_message == 'Testing':
            return 'info'
        else:
            maxScore = obj.problem.maxScore

    elif type(obj) is TestResult:
        maxScore = obj.test.score
    
    if obj.score == maxScore:
        return 'success'
    elif obj.score == 0:
        return 'danger'
    else:
        return 'warning'

