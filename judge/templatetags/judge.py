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
            'name': 'preview',
             'url': reverse('judge:problem_details', args = (problem_pk,)),
             'text': 'Preview'
        },{
            'name': 'statement',
            'url': reverse('judge:problem_edit', args = (problem_pk,)),
            'text': 'Edit statement'
        }, {
            'name': 'media',
            'url': reverse('judge:problem_media', args = (problem_pk,)),
            'text': 'Upload Media'
        }, {
            'name': 'tests',
            'url': reverse('judge:test_list', args = (problem_pk,)),
            'text': 'Edit tests'
        }, {
            'name': 'test_new',
            'url': reverse('judge:test_new', args = (problem_pk,)),
            'text': 'Add tests'
        }, {
            'name': 'test_groups',
            'url': reverse('judge:test_group_list', args = (problem_pk,)),
            'text': 'Edit test groups'
        }, {
            'name': 'checker',
            'url': reverse('judge:problem_checker', args = (problem_pk,)),
            'text': 'Configure a custom checker'
        }, {
            'name': 'visibility',
            'url': reverse('judge:problem_visibility', args= (problem_pk,)),
            'text': 'Change visibility'
        }, {
            'name': 'retest',
            'url': reverse('judge:problem_retest', args = (problem_pk,)),
            'text': 'Retest problem'
        }, {
            'name': 'delete',
            'url': reverse('judge:problem_delete', args = (problem_pk,)),
            'text': 'Delete problem'
        }
     ]
    }

@register.inclusion_tag('judge/problem_admin_panel.html', takes_context = True)
def problem_admin_panel(context, *args, **kwargs):
    user = context.request.user

    pageContext = {}
    if 'problem' in kwargs:
        pageContext['problem'] = kwargs['problem']
        pageContext['has_permission'] = user.has_perm('judge.change_problem')
    else:
        pageContext['has_permission'] = user.has_perm('judge.add_problem')

    return pageContext

@register.inclusion_tag('judge/test_select.html')
def test_select(problem, **kwargs):
    return {
            'tests': problem.test_set.all(),
            'selected': set(kwargs.get('selected', []))
    }

@register.filter
def status_class(obj, *args, **kwargs):
    if type(obj) is Solution:
        if obj.grader_message == 'Testing' or obj.grader_message == 'In Queue':
            return 'info'

        maxScore = obj.problem.maxScore
        if obj.score == maxScore:
            return 'success'
        elif obj.score == 0:
            return 'danger'
        else:
            return 'warning'

    elif type(obj) is TestResult:
        maxScore = obj.test.score
        if obj.message == 'Accepted':
                if obj.score == maxScore:
                    return 'success'
                else: 
                    return 'warning'
        else:
            return 'danger'
    
    
@register.filter
def tags_url(tags, curTag = ''):
    remTag = False
    tagsStr = ''
    curTag = str(curTag)

    for tag in tags:
        if tag == curTag:
            remTag = True
            continue

        if not tagsStr:
            tagsStr = tag
        else:
            tagsStr += ',' + tag


    if (not remTag) and curTag:
        if not tagsStr:
            tagsStr = curTag
        else:
            tagsStr += ',' + curTag

    if tagsStr:
        return reverse('judge:problem_list_tags', args=(tagsStr,))
    else:
        return reverse('judge:problem_list')
