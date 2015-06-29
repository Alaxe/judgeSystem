from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, permission_required

from users import views

urlpatterns = patterns('',
   url(r'^login/$', views.Login.as_view(), 
       name = 'login'),
   url(r'^register/$', views.Register.as_view(),
       name = 'register'),
   url(r'^user/$', login_required(views.UserDetails.as_view()),
       name = 'user_details'),
   url(r'^logout/$', views.Logout.as_view(),
       name = 'logout'),
   url(r'^passwordreset/$', views.ResetPassword.as_view(),
       name = 'password_reset'),
   url(r'^activate/(?P<code>\w+)/$', views.Confirm.as_view(),
       name = 'activate'),
   url(r'^setpassword/(?P<code>\w+)/$', views.SetPassword.as_view(),
       name = 'set_password'),
)
