from django.urls import path
from . import contest_question_database_views, course_database_views, experiment_file_database_views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    # course file database starts
    path('course-file-database/course/<int:course_id>', course_database_views.CourseView.as_view()),
    path('course-file-database/course/<int:course_id>/count', course_database_views.CourseFileCountView.as_view()),
    path('course-file-database/course/<int:course_id>/<int:file_id>', course_database_views.CourseFileMetaView.as_view()),
    path('course-file-database/course/<int:course_id>/<int:file_id>/file', course_database_views.CourseFileView.as_view()),
    # course file database ends
    # experiment file database starts
    path('experiment-file-database/experiment/<int:experiment_id>', experiment_file_database_views.ExperimentView.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/count', experiment_file_database_views.ExperimentFileCountView.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/<int:file_id>', experiment_file_database_views.ExperimentFileMetaView.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/<int:file_id>/file', experiment_file_database_views.ExperimentFileView.as_view()),
    # experiment file database ends
    # contest question database starts
    path('contest-question-database/question', contest_question_database_views.QuestionView.as_view()),
    path('contest-question-database/question/count', contest_question_database_views.QuestionCountView.as_view()),
    path('contest-question-database/question/<int:question_type>/<int:question_id>', contest_question_database_views.QuestionIdView.as_view()),
    path('contest-question-database/question/random', contest_question_database_views.RandomQuestionView.as_view()),
    # contest question database ends
]
