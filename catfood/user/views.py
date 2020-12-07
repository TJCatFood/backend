from django.shortcuts import render
from django.contrib import auth

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.authentication import BasicAuthentication,SessionAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher
from django.db.models.query import EmptyQuerySet
from .models import *

class DefaultView(APIView):
  authentication_classes = (CatfoodAuthentication,)
  permission_classes = (IsStudent,)
  def get(self, request, format=None):
    return Response('this is the default page')

class LoginView(APIView):
  # def get(self, request, format=None):
  #   if request.session['user_id']:
  #     return Response('login with token sec')
  #   else:
  #     return Response('login without token')

  def post(self, request, format=None):
    user_id = request.POST.get('user_id')
    password = request.POST.get('password')
    # check the user_id
    try:
      user = User.objects.get(user_id=user_id)
    except:
      content = {
        'isSuccess': "false",
        'error': {
          'message': "输入的用户ID不存在"
        }
      }
      return Response(content, status=400)

    # check the password
    if not user.check_password(password):
      content = {
        'isSuccess': "false",
        'error': {
          'message': "用户ID与密码不匹配"
        }
      }
      return Response(content, status=400)

    
    content = {
      'isSuccess': "true",
      'data': {
        'user_id': f"{user.user_id}",
        'realname': f"{user.realname}",
        'email': f"{user.email}",
        'university_id': f"{user.university_id}",
        'school_id': f"{user.school_id}",
        'character': f"{user.character}",
        'personal_id': f"{user.personal_id}",
        'avatar': f"{user.avatar}",
      }
    }
    request.session['user_id'] = user.user_id
    request.session["login"] = True
    # request.session['character']=user.character
    return Response(content)

class LogoutView(APIView):
  authentication_classes = (CatfoodAuthentication,)
  permission_classes = [IsStudent|IsTeachingAssistant|IsTeacher|IsChargingTeacher]

  def post(self, request):
    try:
      del request.session['login']
      del request.session['user_id']
    except KeyError:
      pass
    request.session.flush()
    return Response("logged out")

class RegisterView(APIView):
  permission_classes = (AllowAny,)
  def get(self, request, format=None):
    return Response('the register page')

  def post(self, request, format=None):
    user_id, password = request.POST.get('user_id'), request.POST.get('password')

    if User.objects.filter(user_id=user_id).count() != 0:
      content = {
        'isSuccess': "false",
        'error': {
          'message': "用户ID已被注册"
        }
      }
      return Response(content, status=400)

    realname = request.POST.get('realname')
    email = request.POST.get('email')
    university_id = request.POST.get('university_id')
    school_id = request.POST.get('school_id')
    character = request.POST.get('character')
    personal_id = request.POST.get('personal_id')
    avatar = request.POST.get('avatar')

    if user_id and password:
      User.objects.create(user_id=user_id,password=password,realname=realname,
        email=email, university_id=university_id, school_id=school_id, character=character,
        personal_id=personal_id, avatar=avatar)
      content = {
        'isSuccess' : "true",
        'data' : {
          'message' : "注册成功"
        }
      }
      return Response(content, status=201)
    else:
      content = {
        'isSuccess' : "false",
        'data' : {
          'message' : "缺少用户ID或密码"
        }
      }
      return Response(content, status=400)

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