from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, permission_required

from users import views

args = ('',
   url(r'^login/$', views.Login.as_view(), 
       name = 'login'),
   url(r'^register/$', views.Register.as_view(),
       name = 'register'),
    url(r'^activate/(?P<code>\w+)/$', views.Confirm.as_view(),
       name = 'activate'),
   url(r'^logout/$', views.Logout.as_view(),
       name = 'logout'),

     url(r'^passwordreset/$', views.ResetPassword.as_view(),
       name = 'password_reset'),
   url(r'^setpassword/(?P<code>\w+)/$', views.SetPassword.as_view(),
       name = 'password_set'),

   url(r'^changepassword/$', login_required(views.PasswordChange.as_view()),
       name = 'change_password'),
   url(r'^$', login_required(views.UserDetails.as_view()),
       name = 'details'),
)

#try:
args = args + (
    url(r'^solutions/$', login_required(views.Solutions.as_view()),
        name = 'solutions'),
    url(r'^solutions/page/(?P<page>\d+)/$', login_required(
        views.Solutions.as_view()),
        name = 'solutions_page')
)
#except AttributeError:
    # view does not exist
    #pass

urlpatterns = patterns(*args)
