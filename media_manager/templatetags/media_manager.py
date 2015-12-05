from django import template
from django.core.urlresolvers import reverse

from media_manager.views import MediaUploadForm
from media_manager.models import MediaFile

register = template.Library()

@register.inclusion_tag('media_manager/upload.html', takes_context = True)
def media_upload(context, *args, **kwargs):
    obj = kwargs.get('object')

    media_url = reverse('media_manager:upload', args = (obj._meta.app_label,  
        obj.__class__.__name__.lower(), obj.pk))
    redir_url = context.request.get_full_path()

    return {
        'form': MediaUploadForm(),
        'media_post':  '{0}?redir_url={1}'.format(media_url, redir_url)
    }
