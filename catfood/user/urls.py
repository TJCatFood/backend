from django.urls import path
from user import views
from rest_framework import routers

router = routers.DefaultRouter()
urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('account/', views.AccountView.as_view()),
    path('accounts/', views.AccountsView.as_view()),
    path('account/password/', views.PasswordView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('university/', views.UniversityView.as_view()),
    path('school/', views.SchoolView.as_view()),
    path('courses/', views.CoursesView.as_view())
]
