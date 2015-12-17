from django.conf.urls import patterns, url

from users import views

urlpatterns = [
    url(r'^login/$', views.Login.as_view(), name = 'login'),
    url(r'^register/$', views.Register.as_view(), name = 'register'),
    url(r'^activate/(?P<code>\w+)/$', views.Confirm.as_view(), name = 
        'activate'),
    url(r'^logout/$', views.Logout.as_view(), name = 'logout'),

    url(r'^passwordreset/$', views.ResetPassword.as_view(), name = 
        'password_reset'),
    url(r'^setpassword/(?P<code>\w+)/$', views.SetPassword.as_view(), name = 
        'password_set'),

    url(r'^changepassword/$', views.PasswordChange.as_view(), name = 
        'change_password'),
    url(r'^$', views.UserDetails.as_view(), name = 'details'),

    url(r'^solutions/$', views.Solutions.as_view(), name = 'solutions'),
    url(r'^solutions/page/(?P<page>\d+)/$', views.Solutions.as_view(), name = 
        'solutions_page'),
]
