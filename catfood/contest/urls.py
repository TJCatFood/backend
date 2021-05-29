from django.urls import path
from contest import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
    path('contest', views.ContestView.as_view()),
    path('match/<int:match_id>', views.get_match),
    path('match', views.MatchView.as_view()),
    path('matches/', views.get_matches),
    path('matches/<int:contest_id>', views.MatchesView.as_view()),
    path('matches/student', views.get_matches_student),
    path('matchId', views.get_matchid),
    path('contest/questions/student/<int:contest_id>', views.get_contest_questions_student),
    path('contest/questions/teacher/<int:contest_id>', views.get_contest_questions_teacher),
    path('contest/end', views.get_contest_end),
    path('attend', views.AttendView.as_view()),
]
