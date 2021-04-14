from django.urls import path
from course import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('course-info/', views.courses_list),
    path('course-info/<int:course_id>', views.course_detail),
    path('teach/', views.teach_list),
    path('teach/<int:teach_id>', views.teach_detail),
    path('course-student-info/<int:course_id>', views.get_students_by_course_id)
]
