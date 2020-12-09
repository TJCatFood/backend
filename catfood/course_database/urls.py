from django.urls import path
from . import template, contest_question_database_views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', template.AliveView.as_view()),
    # course file database starts
    path('course-file-database/course/<int:course_id>', template.CourseIdTemplate.as_view()),
    path('course-file-database/course/<int:course_id>/count', template.CourseIdTemplate.as_view()),
    path('course-file-database/course/<int:course_id>/<int:file_id>', template.CourseIdFileIdTemplate.as_view()),
    # course file database ends
    # experiment file database starts
    path('experiment-file-database/experiment/<int:experiment_id>', template.ExperimentIdTemplate.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/count', template.ExperimentIdTemplate.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/<int:file_id>', template.ExperimentIdFileIdTemplate.as_view()),
    # experiment file database ends
    # contest question database starts
    path('contest-question-database/question', contest_question_database_views.QuestionController.as_view()),
    path('contest-question-database/question/count', contest_question_database_views.QuestionCountController.as_view()),
    path('contest-question-database/question/<int:question_type>/<int:question_id>', contest_question_database_views.QuestionPutDeleteController.as_view()),
    # contest question database ends
]
