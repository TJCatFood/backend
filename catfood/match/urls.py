from django.urls import path
from match import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
]
