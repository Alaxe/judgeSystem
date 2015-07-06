from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context = True)
def user_nav(context, *args, **kwargs):
    curPage = kwargs.get('page', '')
    
    pages = [{
        'name': 'details',
        'url': reverse('users:details'),
        'text': 'Details'
    }, {
        'name': 'change_password',
        'url': reverse('users:change_password'),
        'text': 'Change password'
    }]

    try:
        from users.views import Solutions
        pages.append({
            'name': 'solutions',
            'url': reverse('users:solutions'),
            'text': 'Solutions'
        })
    except ImportError:
        pass

    context = template.Context({
        'curPage': curPage,
        'pages': pages
    })

    curTemplate = template.loader.get_template('judge/problem_edit_nav.html')
    return curTemplate.render(context)

