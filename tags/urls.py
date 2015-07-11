from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, permission_required

from tags import views

urlpatterns = patterns('',
    url(r'^new/$', permission_required(
        'tags.add_tag')(views.TagNew.as_view()),
        name = 'tag_new'),
    url(r'^(?P<pk>\d+)/edit/$', permission_required(
        'tags.change_tag')(views.TagEdit.as_view()),
        name = 'tag_edit'),
    url(r'^(?P<pk>\d+)/delete/$', permission_required(
        'tags.delete_tag')(views.TagDelete.as_view()),
        name = 'tag_delete'),
    url(r'^$', permission_required(
        'tags.change_tag')(views.TagList.as_view()),
        name = 'tag_list'),
)
