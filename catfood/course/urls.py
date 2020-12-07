from django.urls import path
from course import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('course-info/', views.courses_list),
    path('course-info/<int:course_id>', views.course_detail)
]
