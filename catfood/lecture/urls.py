from django.urls import path
from . import views, templates, course_chapter_description_views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.AliveView.as_view()),
    # course homework starts
    path('course-homework/<int:course_id>/homework/', templates.CourseIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>', templates.CourseIdHomeworkIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/count', templates.CourseIdHomeworkIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file', templates.CourseIdHomeworkIdTemplate.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file/<int:homework_file_id>', templates.CIHIHFI.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file/<int:homework_file_id>/score', templates.CIHIHFI.as_view()),
    # course homework ends
    # course chapter description starts
    path('course-chapter-description/<int:course_id>/chapter/', course_chapter_description_views.ChapterDescriptionView.as_view()),
    path('course-chapter-description/<int:course_id>/chapter/<int:course_chapter_id>', course_chapter_description_views.ChapterDescriptionIdView.as_view()),
    # course chapter description ends
]
