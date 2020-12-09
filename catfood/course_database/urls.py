from django.urls import path
from . import templates, contest_question_database_views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', templates.AliveView.as_view()),
    # course file database starts
    path('course-file-database/course/<int:course_id>', templates.CourseIdTemplate.as_view()),
    path('course-file-database/course/<int:course_id>/count', templates.CourseIdTemplate.as_view()),
    path('course-file-database/course/<int:course_id>/<int:file_id>', templates.CourseIdFileIdTemplate.as_view()),
    # course file database ends
    # experiment file database starts
    path('experiment-file-database/experiment/<int:experiment_id>', templates.ExperimentIdTemplate.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/count', templates.ExperimentIdTemplate.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/<int:file_id>', templates.ExperimentIdFileIdTemplate.as_view()),
    # experiment file database ends
    # contest question database starts
    path('contest-question-database/question', contest_question_database_views.QuestionView.as_view()),
    path('contest-question-database/question/count', contest_question_database_views.QuestionCountView.as_view()),
    path('contest-question-database/question/<int:question_type>/<int:question_id>', contest_question_database_views.QuestionIdView.as_view()),
    # contest question database ends
]
