from django.urls import path
from contest import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
    path('contest', views.ContestView.as_view()),
    path('match/<int:match_id>', views.get_match),
    path('matches/', views.get_matches),
    path('matches/<int:contest_id>', views.MatchesView.as_view()),
    path('matches/student', views.get_matches_student),
    path('matchid', views.get_matchid),
    path('contest/question/<int:contest_id>', views.get_contest_questions),
    path('contest/end', views.get_contest_end),
]
