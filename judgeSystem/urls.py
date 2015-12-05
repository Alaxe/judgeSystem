from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'judgeSystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('judge.urls', namespace = 'judge')),
    url(r'^account/', include('users.urls', namespace = 'users')),
    url(r'^blog/', include('blog.urls', namespace = 'blog')),
    url(r'^media_manager/', include('media_manager.urls', 
        namespace = 'media_manager')),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
