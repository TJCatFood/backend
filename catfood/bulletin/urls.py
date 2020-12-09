from django.urls import path
from . import views, templates
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.AliveView.as_view()),
    # course announcement starts
    path('<int:course_id>/announcement', views.AnnouncementView.as_view()),
    path('<int:course_id>/announcement/count', views.AnnouncementCountView.as_view()),
    path('<int:course_id>/announcement/<int:announcement_id>', views.AnnouncementIdView.as_view()),
    # course announcement ends
]
