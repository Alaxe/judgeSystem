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

class PostBase(View):
    template_name = 'blog/post_edit.html'
    title = 'Edit blog post'

    def get_response(self, request, form = BlogPostForm(), pk = None):
        context = {
            'title': self.title,
            'form': form,
            'pk': pk
        }
        return render(request, self.template_name, context)

    @abc.abstractmethod
    def get_blog_post_form(self, *, request, pk):
        pass

    @abc.abstractmethod
    def save_blog_post(self, *args, **kwargs):
        pass

    def post(self, request, pk = None):
        form = self.get_blog_post_form(request = request, pk = pk)

        if not form.is_valid():
            return self.get_response(request, form = form, pk = pk)
        else:
            post = self.save_blog_post(request = request, form = form, pk = pk)
            return redirect(reverse('blog:post_details', args = (post.pk,)))

class PostEdit(PermissionRequiredMixin, PostBase):
    permission_required = 'blog.change_blogpost'

    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)

        if not post.may_edit(request.user):
            raise Http404
        else:
            form = BlogPostForm(instance = post)
            return self.get_response(request, form = form, pk = pk)

    def get_blog_post_form(self, *args, **kwargs):
        post = get_object_or_404(BlogPost, pk = kwargs['pk'])
        return BlogPostForm(kwargs['request'].POST, instance = post)

    def save_blog_post(self, *args, **kwargs):
        return kwargs['form'].save()

class PostNew(PermissionRequiredMixin, PostBase):
    permission_required = 'blog.add_blogpost'
    title = 'New blog post'

    def get(self, request):
        return self.get_response(request)

    def get_blog_post_form(self, *args, **kwargs):
        return BlogPostForm(kwargs['request'].POST)

    def save_blog_post(self, *args, **kwargs):
        post = kwargs['form'].save(commit = False)
        post.author = kwargs['request'].user
        post.save()

        return post


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

        context = {'post': post }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk = pk)
        post.delete()

        messageText = 'Blog post deleted successfully'
        messages.add_message(request, messages.SUCCESS, messageText)

        url = reverse('blog:post_list')
        return HttpResponseRedirect(url)
