from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from blog import views

urlpatterns = [
    url(r'^post/(?P<pk>\d+)/edit/$', views.PostEdit.as_view(),
        name = 'post_edit'),
    url(r'^post/new/$', views.PostNew.as_view(), name = 'post_new'),
    url(r'post/(?P<pk>\d+)/delete/$', views.PostDelete.as_view(),
        name = 'post_delete'),
    url(r'post/(?P<pk>\d+)/media/$', views.PostMedia.as_view(),
        name = 'post_media'),
    url(r'^post/(?P<pk>\d+)/$', views.PostDetails.as_view(),
        name = 'post_details'),

    url(r'^page/(?P<page>\d+)/$', views.PostList.as_view(),
        name = 'post_page'),
    url(r'^$', views.PostList.as_view(),
        name = 'post_list'),
]
