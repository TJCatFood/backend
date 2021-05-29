from django.urls import path
from . import contest_question_database_views, course_database_views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    # course file database starts
    path('course-file-database/course/<int:course_id>', course_database_views.CourseView.as_view()),
    path('course-file-database/course/<int:course_id>/count', course_database_views.CourseFileCountView.as_view()),
    path('course-file-database/course/<int:course_id>/<int:file_id>', course_database_views.CourseFileMetaView.as_view()),
    path('course-file-database/course/<int:course_id>/<int:file_id>/file', course_database_views.CourseFileView.as_view()),
    # course file database ends
    # contest question database starts
    path('contest-question-database/question', contest_question_database_views.QuestionView.as_view()),
    path('contest-question-database/question/count', contest_question_database_views.QuestionCountView.as_view()),
    path('contest-question-database/question/<int:question_type>/<int:question_id>', contest_question_database_views.QuestionIdView.as_view()),
    path('contest-question-database/question/random', contest_question_database_views.RandomQuestionView.as_view()),
    # contest question database ends
]
