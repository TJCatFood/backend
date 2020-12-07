from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
urlpatterns = [
    path('api/', include(router.urls)),
    path('status/', views.CatFoodStatusView.as_view()),
    path('api/v1/contest/', include('contest.urls')),
    path('api/v1/experiment/', include('experiment.urls')),
    path('api/v1/course/', include('course.urls'))
]
