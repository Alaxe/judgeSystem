from django import template
from django.utils import timezone

register = template.Library()

@register.inclusion_tag('blog/post_admin_panel.html', takes_context = True)
def post_admin_panel(context, *args, **kwargs):
    user = context.request.user

    templateContext = {}
    if 'post' in kwargs:
        templateContext['has_permission'] = user.has_perm('blog.change_post')
        templateContext['post'] = kwargs['post']
    else:
        templateContext['has_permission'] = user.has_perm('blog.create_post')
    return templateContext

@register.filter
def post_subheading(post):
    timeStr = post.post_time.strftime('%d %b %Y')
    return timeStr + ' by ' + post.author.username

