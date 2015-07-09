from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import View, TemplateView

from tags.models import Tag

class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

class TagEdit(View):
    template_name = 'tags/tag_new.html'
    title = 'Edit tag'

    def get_response(self, request, form = TagForm(), pk = None):
        context = {
            'form': form,
            'title': self.title,
            'pk': pk
        }
        return render(request, self.template_name, context)

    def get(self, request, pk = None):
        if pk:
            tag = get_object_or_404(Tag, pk = pk)
            form = TagForm(instance = tag)
        else:
            print(request.GET)
            initial = {'category': request.GET.get('category', '')}
            form = TagForm(initial = initial)

        return self.get_response(request, form = form, pk = pk)

    def post(self, request, pk = None):
        if pk:
            obj = get_object_or_404(Tag, pk = pk)
            form = TagForm(request.POST, instance = obj)
        else:
            form = TagForm(request.POST)

        if not form.is_valid():
            return get_response(request, form = form, pk = pk)

        tag = form.save()
        
        messageText = 'Tag saved successfully.'
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('tags:tag_list')
        return HttpResponseRedirect(url)

class TagNew(TagEdit):
    title = 'New tag'

class TagDelete(View):
    template_name = 'tags/tag_delete.html'

    def get(self, request, pk):
        tag = get_object_or_404(Tag, pk = pk)
        
        context = {'tag': tag }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        tag = get_object_or_404(Tag, pk = pk)
        tag.delete()

        messageText = 'Tag has been deleted successfully'
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('tags:tag_list')
        return HttpResponseRedirect(url)

def tags_by_category():
    tags = {}
    for tag in Tag.objects.all():
        if tag.category in tags:
            tags[tag.category].append(tag)
        else:
            tags[tag.category] = [tag]


    awns = []
    for key in tags:
        awns.append((key, tags[key],))
        
    return awns

class TagList(TemplateView):
    template_name = 'tags/tag_list.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(TagList, self).get_context_data(*args, **kwargs)
        context['tags'] = tags_by_category()
        return context
