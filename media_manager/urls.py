from django.conf.urls import url

from media_manager import views

urlpatterns = [
    #url(r'^upload/', views.MediaUpload.as_view(), name = 'upload_empty'),
    url(r'^upload/(?P<app_label>\w+)/(?P<model>\w+)/(?P<id>\d+)/',
        views.MediaUpload.as_view(), name = 'upload')
]
