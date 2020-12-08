from django.urls import path
from course_database import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.AliveView.as_view()),
    # course file database starts
    path('course-file-database/course/<int:course_id>', views.CourseIdTemplate.as_view()),
    path('course-file-database/course/<int:course_id>/count', views.CourseIdTemplate.as_view()),
    path('course-file-database/course/<int:course_id>/<int:file_id>', views.CourseIdFileIdTemplate.as_view()),
    # course file database ends 
    # experiment file database starts
    path('experiment-file-database/experiment/<int:experiment_id>', views.ExperimentIdTemplate.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/count', views.ExperimentIdTemplate.as_view()),
    path('experiment-file-database/experiment/<int:experiment_id>/<int:file_id>', views.ExperimentIdFileIdTemplate.as_view()),
    # experiment file database ends
    # contest question database starts
    path('contest-question-database/question', views.QuestionController.as_view()),
    path('contest-question-database/question/count', views.QuestionCountController.as_view()),
    path('contest-question-database/question/<int:question_type>/<int:question_id>', views.QuestionPutController.as_view()),
    # contest question database ends
]