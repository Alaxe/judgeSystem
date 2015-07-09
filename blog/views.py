from django.contrib import messages
from django.core.paginator import InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import View, DetailView, TemplateView

from blog.models import BlogPost

class PostForm(ModelForm):
    class Meta:
        model = BlogPost
        exclude = ['author', 'post_time']

class PostEdit(View):
    template_name = 'blog/post_edit.html'
    title = 'Edit blog post'

    def get_response(self, request, form = PostForm(), pk = None):
        context = {
            'title': self.title,
            'form': form,
            'pk': pk
        }
        return render(request, self.template_name, context)

    def get(self, request, pk = None):
        if pk:
            kwargs = {'pk': pk}
            if not request.user.has_perm('blog.edit_foreign_post'):
                kwargs['author'] = request.user

            post = get_object_or_404(BlogPost, **kwargs)

            form = PostForm(instance = post)
            return self.get_response(request, form = form, pk = pk)
        else:
            return self.get_response(request)

    def post(self, request, pk = None):
        if pk:
            post = get_object_or_404(BlogPost, pk = pk)
            form = PostForm(request.POST, instance = post)
        else:
            form = PostForm(request.POST)

        if not form.is_valid():
            return self.get_response(request, form = form, pk = pk)

        post = form.save(commit = False)
        post.author = request.user
        post.save()
        
        url = reverse('blog:post_details', args = (post.pk,))
        return HttpResponseRedirect(url)       

class PostNew(PostEdit):
    title = 'New blog post'

class PostDetails(DetailView):
    model = BlogPost
    context_object_name = 'post'
    template_name = 'blog/post_details.html'

class PostList(TemplateView):
    template_name = 'blog/post_list.html'

    def get_context_data(self, page = 1, **kwargs):
        posts = BlogPost.objects.all()
        paginator = Paginator(posts, 5)
        
        try:
            curPage = paginator.page(page)
        except InvalidPage:
            raise Http404

        context = super(PostList, self).get_context_data(**kwargs)
        context['page'] = curPage

        return context

class PostDelete(View):
    template_name = 'blog/post_delete.html'

    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)

        context = {'post': post }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)
        post.delete()

        messageText = 'Blog post deleted successfully'
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('blog:post_list')
        return HttpResponseRedirect(url)
