from django import forms
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from media_manager.models import MediaFile

class MediaUploadForm(forms.Form):
    media = forms.FileField(label = 'The media you want to upload')

def get_model(app_label, model, id):
    try:
        model_type = ContentType.objects.get(app_label = app_label, 
                model = model.lower())
        model = model_type.get_object_for_this_type(id = id)

        return model
    except ObjectDoesNotExist:
        raise Http404

class MediaUpload(View):
    def post(self, request, **kwargs):
        form = MediaUploadForm(request.POST, request.FILES)
        model = get_model(kwargs['app_label'], kwargs['model'], kwargs['id'])

        redir_url = request.GET.get('redir_url', '/')
        permStr = '{0}.add_media_to_{1}'.format(model._meta.app_label, 
                model.__class__.__name__.lower())
 
        if not form.is_valid():
            messages.warning(request, 'No file to upload')
        elif not request.user.has_perm(permStr):
            messages.error(request, 'Missing permissions')
        else:
            media = MediaFile(content_object = model,
                media = request.FILES['media'], 
                filename = request.FILES['media'].name)
            media.save()

            messages.success(request, 'Media uploaded successfully')

        return HttpResponseRedirect(redir_url)
