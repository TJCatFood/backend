from django.urls import path
from match import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
    path('start', views.StartView.as_view()),
    path('cancel', views.CancelView.as_view()),
    path('userindex', views.IndexView.as_view()),
    path('ready', views.ReadyView.as_view()),
]
