from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.AliveView.as_view()),
    # course announcement starts
    path('<int:course_id>/announcement', views.AnnouncementController.as_view()),
    path('<int:course_id>/announcement/count', views.CourseIdTemplate.as_view()),
    path('<int:course_id>/announcement/<int:announcement_id>', views.CourseIdAnnouncementIdTemplate.as_view()),
    # course announcement ends
]
