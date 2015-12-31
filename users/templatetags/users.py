from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.inclusion_tag('judge/problem_edit_nav.html', takes_context = True)
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

    if context.request.user.has_perm('auth.change_group'):
        pages.append({
            'name': 'manage',
            'url': reverse('users:manage'),
            'text': 'Manage users'
        })

    return {
        'curPage': curPage,
        'pages': pages
    }


