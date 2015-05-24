from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, permission_required

from judge import views

urlpatterns = patterns('',
    url(r'^problems/$', views.ProblemList.as_view(), 
        name = 'problem_list'),
   url(r'^problems/page/(?P<page_id>\d+)/$', views.ProblemList.as_view(), 
       name = 'problem_page'),

   url(r'^problems/new/', 
       permission_required('judge.add_problem')(views.ProblemNew.as_view()), 
       name = 'problem_new'),
   url(r'^problems/(?P<pk>\d+)/edit/$', permission_required(
       'judge.change_problem')(views.ProblemEdit.as_view()), 
       name = 'problem_edit'),

   url(r'^problems/(?P<pk>\d+)/$', views.ProblemDetails.as_view(), 
       name = 'problem_details'),

   url(r'^problems/(?P<problem_id>\d+)/newtest/$', 
       permission_required('judge.add_test')(views.TestNew.as_view()), 
       name = 'test_new'),
   url(r'^test/(?P<pk>\d+)/edit/$', 
       permission_required('judge.change_test')(views.TestEdit.as_view()),
       name = 'test_edit'),

   url(r'^problems/(?P<pk>\d+)/submit/$', 
       login_required(views.SolutionSubmit.as_view()), 
       name = 'solution_submit'),
   url(r'^solutions/(?P<pk>\d+)/$', views.SolutionDetails.as_view(),
       name = 'solution_details'),

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
