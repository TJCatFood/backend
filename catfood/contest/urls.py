from django.urls import path
from contest import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
    path('contest/', views.ContestView.as_view()),
    path('match/<int:match_id>', views.get_match),
    path('matches/', views.get_matches),
    path('matches/<int:contest_id>', views.MatchesVIew.as_view()),
]
