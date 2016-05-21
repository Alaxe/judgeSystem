import abc

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, \
    PermissionRequiredMixin
from django.core.paginator import InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ModelForm
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View, DetailView, TemplateView

from blog.models import BlogPost

class BlogPostForm(ModelForm):
    class Meta:
        model = BlogPost
        exclude = ['author', 'post_time']

class PostEdit(PermissionRequiredMixin, View):
    permission_required = 'blog.change_blogpost'
    template_name = 'blog/post_edit.html'

    def get_response(self, request, form = BlogPostForm(), post = None):
        context = {
            'form': form,
            'post': post
        }
        return render(request, self.template_name, context)

    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)

        if not post.may_edit(request.user):
            raise Http404
        else:
            form = BlogPostForm(instance = post)
            return self.get_response(request, form = form, post = post)

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)
        form = BlogPostForm(request.POST, instance = post)

        if not form.is_valid():
            return self.get_response(request, form = form, post = post)
        else:
            form.save()
            return redirect(reverse('blog:post_details', args = (post.pk,)))

class PostNew(PermissionRequiredMixin, View):
    permission_required = 'blog.add_blogpost'

    def get(self, request):
        post = BlogPost.objects.create(author = request.user)
        return redirect(reverse('blog:post_edit', args = (post.pk,)))

class PostMedia(PermissionRequiredMixin, TemplateView):
    permission_required = 'blog.add_media_to_blogpost'
    template_name = 'blog/post_media.html'

    def get_context_data(self, **kwargs):
        context = super(PostMedia, self).get_context_data(**kwargs)
        context['post'] = get_object_or_404(BlogPost, pk = kwargs['pk'])

        if not context['post'].may_edit(self.request.user):
            raise Http404

        return context

class PostDetails(DetailView):
    model = BlogPost
    context_object_name = 'post'
    template_name = 'blog/post_details.html'

class PostList(TemplateView):
    template_name = 'blog/post_list.html'

    def get_context_data(self, page = 1, **kwargs):
        postsQ = Q(public = True)
        if self.request.user.is_authenticated():
            postsQ |= Q(public = False, author = self.request.user)

        if self.request.user.has_perm('blog.change_foreign_blogpost'):
            postsQ = Q()

        posts = BlogPost.objects.filter(postsQ)
        paginator = Paginator(posts, 5)
        
        try:
            curPage = paginator.page(page)
        except InvalidPage:
            raise Http404

        context = super(PostList, self).get_context_data(**kwargs)
        context['page'] = curPage

        return context

class PostDelete(PermissionRequiredMixin, View):
    permission_required = 'blog.delete_blogpost'
    template_name = 'blog/post_delete.html'

    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)
        if not post.may_edit(request.user):
            raise Http404

        context = {
            'post': post
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)
        post.delete()

        messages.success(request, 'Blog post deleted successfully')
        return redirect(reverse('blog:post_list'))
