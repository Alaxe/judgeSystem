from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from media_manager.views import MediaUploadForm
from media_manager.models import MediaFile

register = template.Library()

@register.inclusion_tag('media_manager/upload.html', takes_context = True)
def media_upload(context, object):
    media_url = reverse('media_manager:upload', args = (object._meta.app_label,
        object.__class__.__name__.lower(), object.pk))
    redir_url = context.request.get_full_path()

    return {
        'form': MediaUploadForm(),
        'media_post':  '{0}?redir_url={1}'.format(media_url, redir_url)
    }

@register.inclusion_tag('media_manager/list.html')
def media_list(object):
    model_type = ContentType.objects.get(app_label = object._meta.app_label,
        model = object.__class__.__name__.lower())

    media_list = MediaFile.objects.filter(content_type = model_type, 
            object_id = object.id)

    return {
        'media_list': media_list
    }
