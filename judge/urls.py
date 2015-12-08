from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from judge import views

urlpatterns = [
    url(r'^$', views.ProblemList.as_view(), 
        name = 'problem_list'),
    url(r'^problems/page/(?P<page>\d+)/$', views.ProblemList.as_view(), 
        name = 'problem_page'),
    url(r'^problems/tags/(?P<tags>[\w ]+(,[\w ]+)*)/$', 
        views.ProblemList.as_view(), name = 'problem_list_tags'),
    url(r'^problems/tags/(?P<tags>[\w ]+(,[\w ]+)*)/page/(?P<page>\d+)/$', 
        views.ProblemList.as_view(), name = 'problem_list_tags_page'),
    url(r'^problems/filter/$', views.ProblemFilter.as_view(),
        name = 'problem_filter'),

    url(r'^problems/new/', permission_required(
        'judge.add_problem')(views.ProblemNew.as_view()), 
        name = 'problem_new'),
    url(r'^problems/(?P<pk>\d+)/edit/$', permission_required(
        'judge.change_problem')(views.ProblemEdit.as_view()), 
        name = 'problem_edit'),
    url(r'^problems/(?P<pk>\d+)/delete/$', permission_required(
       'judge.delete_problem')(views.ProblemDelete.as_view()),
       name = 'problem_delete'),
    url(r'^problems/(?P<pk>\d+)/media/$', permission_required(
        'judge.add_media_to_problem')(views.ProblemMedia.as_view()),
        name = 'problem_media'),
    url(r'^problems/(?P<pk>\d+)/retest/$', permission_required(
       'judge.problem_retest')(views.ProblemRetest.as_view()),
       name = 'problem_retest'),
    url(r'^problems/(?P<pk>\d+)/visibility/$', permission_required(
        'judge.problem_visibility')(views.ProblemVisibility.as_view()),
        name = 'problem_visibility'),
    url(r'^problems/(?P<pk>\d+)/checker/$', permission_required(
        'judge.change_problem')(views.ProblemChecker.as_view()),
        name = 'problem_checker'),

    url(r'^problems/(?P<pk>\d+)/$', views.ProblemDetails.as_view(), 
       name = 'problem_details'),

    url(r'^problems/(?P<problem_id>\d+)/newtest/$', permission_required(
       'judge.add_test')(views.TestNew.as_view()), 
       name = 'test_new'),
    url(r'^problems/(?P<problem_id>\d+)/tests/$', permission_required(
       'judge.change_problem')(views.TestList.as_view()),
       name = 'test_list'),
    url(r'^test/(?P<pk>\d+)/edit/$', permission_required(
       'judge.change_test')(views.TestEdit.as_view()),
       name = 'test_edit'),
    url(r'^test/(?P<ids>\d+(,\d+)*)/delete/$', permission_required(
        'judge.delete_test')(views.TestDelete.as_view()),
        name = 'test_delete'),
    url(r'^test/(?P<pk>\d+)/input/$', permission_required(
        'judge.view_test')(views.TestInput.as_view()),
        name = 'test_input'),
    url(r'^test/(?P<pk>\d+)/output/$', permission_required(
        'judge.view_test')(views.TestOutput.as_view()),
        name = 'test_output'),

    url(r'^problems/(?P<problem_id>\d+)/newtestgroup/$',
            views.TestGroupNew.as_view(), name = 'test_group_new'),
    url(r'^problems/(?P<problem_id>\d+)/testgroups/$',
            views.TestGroupList.as_view(), name = 'test_group_list'),
    url(r'^testgroup/(?P<pk>\d+)/edit/$',
            views.TestGroupEdit.as_view(), name = 'test_group_edit'),
    url(r'^testgroup/(?P<pk>\d+)/delete/$',
            views.TestGroupDelete.as_view(), name = 'test_group_delete'),

    url(r'^problems/(?P<pk>\d+)/submit/$', login_required(
        views.SolutionSubmit.as_view()), 
        name = 'solution_submit'),
    url(r'^solutions/(?P<pk>\d+)/$', login_required(
        views.SolutionDetails.as_view()),
        name = 'solution_details'),
    url(r'^solutions/(?P<pk>\d+)/source/$', login_required(
        views.SolutionSource.as_view()),
        name = 'solution_source'),
]
