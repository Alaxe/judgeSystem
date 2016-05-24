from django import template
from django.core.urlresolvers import reverse

from judge.models import Solution, TestResult, TestGroupResult

register = template.Library()

@register.inclusion_tag('judge/problem_edit_nav.html', takes_context = True)
def problem_edit_nav(context, *args, **kwargs):
    page = kwargs.get('page', '')
    problem_pk = context['problem'].pk
    
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
            'name': 'grading',
            'url': reverse('judge:problem_grading', args = (problem_pk,)),
            'text': 'Configure grading'
        }, {
            'name': 'visibility',
            'url': reverse('judge:problem_visibility', args= (problem_pk,)),
            'text': 'Change visibility'
        }, {
            'name': 'retest',
            'url': reverse('judge:problem_retest', args = (problem_pk,)),
            'text': 'Retest problem'
        }, {
            'name': 'export',
            'url': reverse('judge:problem_export', args = (problem_pk,)),
            'text': 'Export'
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
        pageContext['may_import'] = user.has_perm('judge.import_problem')

    return pageContext

@register.inclusion_tag('judge/test_select.html')
def test_select(tests, **kwargs):
    return {
            'tests': tests,
            'selected': set(kwargs.get('selected', [])),
            'select_class': 'test-select' + str(kwargs.get('select_class', ''))
    }

@register.inclusion_tag('judge/solution_list.html')
def list_solutions(solutions, **kwargs):
    return {
        'solutions': solutions,
        'show_problem': kwargs.get('show_problem', False)
    }

@register.inclusion_tag('judge/tag_select.html')
def tag_select():
    return {}

@register.filter
def status_class(obj, *args, **kwargs):
    if type(obj) is Solution:
        if obj.grader_message == 'Testing' or obj.grader_message == 'In Queue':
            return 'info'

        if obj.score == obj.problem.max_score:
            return 'success'
        elif obj.score == 0:
            return 'danger'
        else:
            return 'warning'

    elif type(obj) is TestResult:
        return 'success' if obj.passed else 'danger'
    elif type(obj) is TestGroupResult:
        return 'success' if obj.passed else 'danger'
    else: 
        return ''
    
    
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
