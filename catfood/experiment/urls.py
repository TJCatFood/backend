from django.urls import path
from experiment import views
from experiment import experiment_case_views as case_views
from experiment import course_case_views
from experiment import assignments_views
from experiment import statistics_views

from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.TestView.as_view()),
    path('experiment-database/list/', case_views.experiment_case_list),
    path('experiment-database/detail/<int:pk>', case_views.experiment_case_detail),
    path('course-cases/list/<int:course_id>', course_case_views.course_case_list),
    path('course-cases/detail/<int:pk>', course_case_views.course_case_detail),
    path('student/case/detail/<int:course_case_id>', course_case_views.student_get_case_detail),
    path('assignments/student/list/', assignments_views.assignment_student_list),
    path('assignments/student/detail/<int:pk>',
         assignments_views.assignment_student_detail),
    path('assignments/teacher/list/<int:course_case_id>',
         assignments_views.assignment_teacher_list),
    path('assignments/teacher/detail/<int:pk>', assignments_views.assignment_teacher_detail),
    path('teacher/assignment/detail/<int:submission_id>', assignments_views.teacher_get_assignment_detail),
    path('teacher/assignment/public/<int:course_case_id>', assignments_views.teacher_public_all_assignments),
    path('statistics/course-case/<int:course_case_id>', statistics_views.get_course_case_statistics),
]
