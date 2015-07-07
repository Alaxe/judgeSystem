from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def post_subheading(post):
    timeStr = post.post_time.strftime('%d %b %Y')
    return timeStr + ' by ' + post.author.username

