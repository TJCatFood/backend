from django.urls import path
from experiment import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
    path('experiment-database/list/', views.experiment_case_list),
    path('experiment-database/detail/<int:pk>', views.experiment_case_detail),
    path('course-cases/list/<int:course_id>', views.course_case_list),
    path('course-cases/detail/<int:pk>', views.course_case_detail),
    path('assignments/student/list/', views.assignment_student_list),
    path('assignments/student/detail/<int:pk>',
         views.assignment_student_detail),
    path('assignments/teacher/list/<int:course_case_id>',
         views.assignment_teacher_list),
    path('assignments/teacher/detail/<int:pk>', views.assignment_teacher_detail)
]
