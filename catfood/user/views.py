from django.shortcuts import render
from django.contrib import auth

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.authentication import BasicAuthentication,SessionAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from user.authentication import ExampleAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from .models import *

class DefaultView(APIView):

  def get(self, request, format=None):
    return Response('this is the default page')

class LoginView(APIView):
  authentication_classes = (BasicAuthentication,SessionAuthentication)
  permission_classes = (AllowAny,)

  def get(self, request, format=None):
    if request.session.get("login") == "success":
      return Response('login with token sec')
    else:
      return Response('login without token')

  def post(self, request, format=None):
    user_id = request.POST.get('user_id')
    password_digest = request.POST.get('password_digest')
    # user = auth.authenticate(request, username=user_id, password=password_digest)
    # left the authenticate logic undone
    # read from db
    isSuccess = 'true'
    request.session["login"]="success"
    content = {
      'isSuccess' : f"{isSuccess}",
      'data' : {
        'user_id' : f"{user_id}"
      }
    }
    return Response(content)

class LogoutView(APIView):
  # authentication_classes = (BasicAuthentication,SessionAuthentication)
  # permission_classes = (IsAuthenticated,)
  authentication_classes = [ExampleAuthentication]
  permission_classes = [IsStudent|IsTeachingAssistant|IsTeacher|IsChargingTeacher]

  def post(self, request):
    #the logout job
    return Response("logged out")

class RegisterView(APIView):

  def get(self, request, format=None):
    return Response('the register page')

  def post(self, request, format=None):
    username, password, realname = request.POST.get('username'), request.POST.get('password'), request.POST.get('realname')
    if username and password:
      models.User.objects.create(username=username,password=password,realname=realname)
      content = {
        "realname" : f"{realname}"
      }
      return Response(content)
    else:
      return Response('Error Register')

class AccountView(APIView):

  def get(self, request, user_id, format=None):#different with APIdoc
    return Response('the info of user ' + user_id)

  def patch(self, request, user_id, format=None):
    #TODO： User Authentication
    #different with APIdoc
    isSuccess = 'true'
    content = {
      'isSuccess' : f"{isSuccess}",
      'data' : {
        'user_id' : f"{user_id}"
      }
    }
    return Response(content)

class PasswordView(APIView):
  authentication_classes = (BasicAuthentication,SessionAuthentication)
  permission_classes = (IsAuthenticated,)

  def get(self, request, format:None):
    return Response('this is the password changing page')

  def patch(self, request, format:None):
    #different with APIdoc
    #TODO： User Authentication
    content = {
      'isSuccess' : 'true',
      'data' : {
        'message' : 'password changed successfully'
      }
    }
    return Response(content)

class AccountsView(APIView):
  def get(self, request, format:None):
    return Response('this is the accounts page')

  def post(self, request, format=None):
    #TODO： User Authentication
    content = {
      'isSuccess' : 'true',
      'data' : {
        'message' : 'accounts appended successfully'
      }
    }
    return Response(content)