from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'judgeSystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

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
