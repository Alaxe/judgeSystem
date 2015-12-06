from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from blog import views

urlpatterns = [
    url(r'^post/(?P<pk>\d+)/edit/$', permission_required(
        'blog.change_blogpost')(views.PostEdit.as_view()),
        name = 'post_edit'),
    url(r'^post/new/$', permission_required(
        'blog.add_blogpost')(views.PostNew.as_view()),
        name = 'post_new'),
    url(r'post/(?P<pk>\d+)/delete/$', permission_required(
        'blog.delete_blogpost')(views.PostDelete.as_view()),
        name = 'post_delete'),
    url(r'^post/(?P<pk>\d+)/$', views.PostDetails.as_view(),
        name = 'post_details'),

    url(r'^page/(?P<page>\d+)/$', views.PostList.as_view(),
        name = 'post_page'),
    url(r'^$', views.PostList.as_view(),
        name = 'post_list'),
]
