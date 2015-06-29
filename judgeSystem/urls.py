from django.conf.urls import patterns, include, url
from django.contrib import admin

from judge import urls
from users import urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'judgeSystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^judge/', include('judge.urls', namespace = 'judge')),
    url(r'^account/', include('users.urls', namespace = 'users')),
)
