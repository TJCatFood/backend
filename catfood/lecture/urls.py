from django.urls import path
from . import views, templates, course_chapter_description_views, course_homework_views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.AliveView.as_view()),
    # course homework starts
    path('course-homework/<int:course_id>/homework/', course_homework_views.HomeworkView.as_view()),
    path('course-homework/<int:course_id>/homework/count', course_homework_views.HomeworkCountView.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>', course_homework_views.HomeworkDataView.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file', course_homework_views.HomeworkDataFileView.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file/count', course_homework_views.HomeworkDataFileCountView.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file/<int:homework_file_id>', course_homework_views.HomeworkFileView.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/file/uploader/<int:file_uploader>', course_homework_views.HomeworkFileUploaderView.as_view()),
    path('course-homework/<int:course_id>/homework/<int:homework_id>/score/<int:student_id>', course_homework_views.HomeworkScoreView.as_view()),
    # course homework ends
    # course chapter description starts
    path('course-chapter-description/<int:course_id>/chapter/', course_chapter_description_views.ChapterDescriptionView.as_view()),
    path('course-chapter-description/<int:course_id>/chapter/<int:course_chapter_id>', course_chapter_description_views.ChapterDescriptionIdView.as_view()),
    # course chapter description ends
]
