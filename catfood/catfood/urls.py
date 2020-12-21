from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
urlpatterns = [
    path('api/', include(router.urls)),
    path('status/', views.CatFoodStatusView.as_view()),
    path('api/v1/contest/', include('contest.urls')),
    path('api/v1/experiment/', include('experiment.urls')),
    path('api/v1/course/', include('course.urls')),
    path('api/v1/user/', include('user.urls')),
    # includes course file database and experiment file database
    path('api/v1/course-database/', include('course_database.urls')),
    # includes course homework and course description
    path('api/v1/lecture/', include('lecture.urls')),
    # includes course bulletin
    path('api/v1/course-bulletin/', include('bulletin.urls')),
    path('api/v1/match/', include('match.urls')),
    path('api/v1/grade/', include('grade.urls')),
    # includes avatar
    path('api/v1/avatar/', include('avatar.urls')),
]
