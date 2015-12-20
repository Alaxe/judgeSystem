from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask, \
    TaskState, WorkerState
from taggit.models import Tag

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('judge.urls', namespace = 'judge')),
    url(r'^account/', include('users.urls', namespace = 'users')),
    url(r'^blog/', include('blog.urls', namespace = 'blog')),
    url(r'^media_manager/', include('media_manager.urls', 
        namespace = 'media_manager')),
]
if settings.DEBUG:
    from django.views import static
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', static.serve, {
        'document_root': settings.MEDIA_ROOT})]

admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(Tag)

admin.site.login = login_required(admin.site.login)
