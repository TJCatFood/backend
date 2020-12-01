from django.urls import path
from user import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('', views.DefaultView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('register/', views.post_register),
    path('account/<int:user_id>', views.AccountView.as_view()),
    path('accounts/', views.post_accounts),
    path('account/password/', views.patch_change_password)
]