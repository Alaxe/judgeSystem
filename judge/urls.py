from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, permission_required

from judge import views

urlpatterns = patterns('',
    url(r'^problems/$', views.ProblemList.as_view(), 
        name = 'problem_list'),
   url(r'^problems/page/(?P<page>\d+)/$', views.ProblemList.as_view(), 
       name = 'problem_page'),

   url(r'^problems/new/', permission_required(
       'judge.add_problem')(views.ProblemNew.as_view()), 
       name = 'problem_new'),
   url(r'^problems/(?P<pk>\d+)/edit/$', permission_required(
       'judge.change_problem')(views.ProblemEdit.as_view()), 
       name = 'problem_edit'),
   url(r'^problems/(?P<pk>\d+)/delete/$', permission_required(
       'judge.delete_problem')(views.ProblemDelete.as_view()),
       name = 'problem_delete'),
   url(r'^problems/(?P<pk>\d+)/global/$', permission_required(
       'judge.change_test')(views.ProblemGlobal.as_view()),
       name = 'problem_global'), 
   url(r'^problems/(?P<pk>\d+)/retest/$', permission_required(
       'judge.retest_problem')(views.ProblemRetest.as_view()),
       name = 'problem_retest'),


   url(r'^problems/(?P<pk>\d+)/$', views.ProblemDetails.as_view(), 
       name = 'problem_details'),

   url(r'^problems/(?P<problem_id>\d+)/newtest/$', 
    permission_required('judge.add_test')(views.TestNew.as_view()), 
       name = 'test_new'),
   url(r'^problems/(?P<pk>\d+)/tests/$', permission_required(
       'judge.change_problem')(views.TestList.as_view()),
       name = 'test_list'),
   url(r'^test/(?P<pk>\d+)/edit/$', permission_required(
       'judge.change_test')(views.TestEdit.as_view()),
       name = 'test_edit'),
   url(r'^test/(?P<pk>\d+)/delete/$', permission_required(
           'judge.delete_test')(views.TestDelete.as_view()),
       name = 'test_delete'),

   url(r'^problems/(?P<pk>\d+)/submit/$', login_required(
       views.SolutionSubmit.as_view()), 
       name = 'solution_submit'),
   url(r'^solutions/(?P<pk>\d+)/$', views.SolutionDetails.as_view(),
       name = 'solution_details'),
)
