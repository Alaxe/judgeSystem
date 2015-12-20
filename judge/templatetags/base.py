from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.inclusion_tag('judgeSystem/navbar.html', takes_context = True)
def base_nav(context, *args, **kwargs):
    page = kwargs.get('page', '')

    navLeft = [{
        'name': 'blog',
        'text': 'Blog',
        'url': reverse('blog:post_list')
    }, {
        'name': 'judge',
        'text': 'Problems',
        'url': reverse('judge:problem_list')
    }]

    user = context.get('user', None)
    if user.is_staff:
        navLeft.append({
            'name': 'admin',
            'text': 'Admin',
            'url': '/admin/'
        })

    if user.is_authenticated():
        navRight = [{
            'name': 'user_details',
            'text': user.username,
            'url': reverse('users:details')
        }, {
            'name': 'logout',
            'text': 'Log out',
            'url': reverse('users:logout')
        }]
    else:
        navRight =  [{
            'name': 'login',
            'text': 'Log in',
            'url': '{0}?next={1}'.format(reverse('users:login'),
                context.request.get_full_path()) 
        }, {
            'name': 'register',
            'text': 'Register',
            'url': reverse('users:register')
        }]
        if page == 'login':
            navRight[0]['url'] = context.request.get_full_path()


    return {
        'curPage': page,
        'navLeft': navLeft,
        'navRight': navRight
    }
