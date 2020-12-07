from django.urls import path
from experiment import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
    path('experiment-database/', views.experiment_case_list),
    path('experiment-database/<int:pk>', views.experiment_case_detail),
]
