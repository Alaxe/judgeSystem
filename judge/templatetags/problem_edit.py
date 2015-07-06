from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context = True)
def problem_edit_nav(context, *args, **kwargs):
    
    page = kwargs.get('page', '')

    problem_pk = context['problem_pk']

    context = template.Context({
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
            'name': 'delete',
            'url': reverse('judge:problem_delete', args = (problem_pk,)),
            'text': 'Delete problem'
        }
     ]
    })


    curTemplate = template.loader.get_template('judge/problem_edit_nav.html')
    return curTemplate.render(context)
