from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.AliveView.as_view()),
    # course homework starts
    path('course-homework/<int:course_id>/homework/', views.CourseIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>', views.CourseIdHomeworkIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/count', views.CourseIdHomeworkIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file', views.CourseIdHomeworkIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file/<int:homework_file_id>', views.CourseIdHomeworkIdHomeworkFileIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file/<int:homework_file_id>/score', views.CourseIdHomeworkIdHomeworkFileIdTemplate.as_view()),
    # course homework ends
    # course chapter description starts
    path('course-chapter-description/<int:course_id>/chapter/', views.CourseIdTemplate.as_view()),
    path('course-chapter-description/<int:course_id>/chapter/<int:chapter_id>', views.CourseIdChapterIdTemplate.as_view()),
    # course chapter description ends
]
