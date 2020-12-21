from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('<int:user_id>', views.AvatarView.as_view()),
]
