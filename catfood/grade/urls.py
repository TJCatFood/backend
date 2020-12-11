from django.urls import path
from grade import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('gradeweight/<int:course_id>', views.GradeWeightView.as_view()),
    path('<int:course_id>/<int:student_id>', views.GradeView.as_view()),
    path('grades/<int:course_id>', views.GradesView.as_view()),
    path('bonus/<int:course_id>/<int:student_id>', views.BonusView.as_view()),
]
