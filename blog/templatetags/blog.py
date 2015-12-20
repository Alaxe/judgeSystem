from django import template
from django.utils import timezone
from django.core.urlresolvers import reverse

register = template.Library()

@register.inclusion_tag('blog/post_admin_panel.html', takes_context = True)
def post_admin_panel(context, *args, **kwargs):
    user = context.request.user

    templateContext = {}
    if 'post' in kwargs:
        if kwargs['post'].author == user:
            templateContext['has_permission'] = user.has_perm(
                'blog.change_blogpost')
        else:
            templateContext['has_permission'] = user.has_perm(
                'blog.change_foreign_blogpost')

        templateContext['post'] = kwargs['post']
    else:
        templateContext['has_permission'] = user.has_perm('blog.add_blogpost')
    return templateContext

@register.inclusion_tag('blog/post_edit_nav.html')
def blog_post_edit_nav(*args, **kwargs):
    page = kwargs.get('page', '')
    blog_pk = kwargs.get('pk')

    return {
        'curPage': kwargs.get('page', ''),
        'pages': [{
                'name': 'preview',
                'url': reverse('blog:post_details', args = (blog_pk,)),
                'text': 'Preview blog post'
            }, {
                'name': 'edit',
                'url': reverse('blog:post_edit', args = (blog_pk,)),
                'text': 'Edit blog post'
            }, {
                'name': 'media',
                'url': '#',
                'text': 'Upload Media'
            }, {
                'name': 'delete',
                'url': reverse('blog:post_delete', args = (blog_pk,)),
                'text': 'Delete blog post'
            }
        ]
    }



@register.filter
def post_subheading(post):
    timeStr = post.post_time.strftime('%d %b %Y')
    return timeStr + ' by ' + post.author.username

