from django.shortcuts import render
from django.contrib import auth

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher
from django.db.models.query import EmptyQuerySet
from rest_framework import status
from .models import User, University, School
from .serializers import UniversitySerializer, SchoolSerializer


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        # login with session_id
        if request.session.get("user_id"):
            user_id = request.session['user_id']
            user = User.objects.get(user_id=user_id)
            if request.session.get("password") == user.password:
                content = {
                    'isSuccess': "true",
                    'data': {
                        'user_id': f"{user.user_id}",
                        'realname': f"{user.realname}",
                        'email': f"{user.email}",
                        'university_id': f"{user.university_id.university_name}",
                        'school_id': f"{user.school_id.school_name}",
                        'character': f"{user.character}",
                        'personal_id': f"{user.personal_id}",
                        'avatar': f"{user.avatar}",
                    }
                }
                return Response(content)

        # login with user_id and password
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        # check the user_id
        try:
            user = User.objects.get(user_id=user_id)
        except(Exception):
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
        request.session['password'] = user.password
        request.session["login"] = True
        return Response(content)


class LogoutView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def post(self, request):
        try:
            del request.session['login']
            del request.session['user_id']
        except KeyError:
            pass
        request.session.flush()
        content = {
            'isSuccess': "true",
            'date': {
                'message': "登出成功"
            }
        }
        return Response(content, status=201)


class RegisterView(APIView):
    permission_classes = (AllowAny,)

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
            User.objects.create(user_id=user_id, password=password, realname=realname,
                                email=email, university_id=university_id, school_id=school_id, character=character,
                                personal_id=personal_id, avatar=avatar)
            request.session.flush()
            content = {
                'isSuccess': "true",
                'data': {
                    'message': "注册成功"
                }
            }
            return Response(content, status=201)
        else:
            content = {
                'isSuccess': "false",
                'data': {
                    'message': "缺少用户ID或密码"
                }
            }
            return Response(content, status=400)


class AccountView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, format=None):
        user = request.user
        content = {
            'isSuccess': "true",
            'data': {
                'user_id': f"{user.user_id}",
                'realname': f"{user.realname}",
                'email': f"{user.email}",
                'university_id': f"{user.university_id.university_name}",
                'school_id': f"{user.school_id.school_name}",
                'character': f"{user.character}",
                'personal_id': f"{user.personal_id}",
                'avatar': f"{user.avatar}",
            }
        }
        return Response(content)

    def patch(self, request, format=None):
        user = request.user
        email = request.POST.get("email")
        avatar = request.POST.get("avatar")
        if email:
            user.email = User.objects.normalize_email(email)
        if avatar:
            user.avatar = avatar
        user.save()
        isSuccess = 'true'
        content = {
            'isSuccess': f"{isSuccess}",
            'data': {
                'message': '用户信息更改成功'
            }
        }
        return Response(content, status=200)


class PasswordView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def patch(self, request, format=None):
        user = request.user
        old_password = request.POST.get("old_password")
        if not user.check_password(old_password):
            content = {
                'isSuccess': "false",
                'error': {
                    'message': "旧密码错误"
                }
            }
            return Response(content, status=400)
        password = request.POST.get("password")
        # User.objects.change_password(user.user_id, password)
        user.set_password(password)
        user.save()
        request.session.flush()
        content = {
            'isSuccess': 'true',
            'data': {
                'message': '密码更改成功'
            }
        }
        return Response(content, status=200)


class AccountsView(APIView):
    def get(self, request, format=None):
        return Response('this is the accounts page')

    def post(self, request, format=None):
        # TODO： User Authentication
        content = {
            'isSuccess': 'true',
            'data': {
                'message': 'accounts appended successfully'
            }
        }
        return Response(content)


class UniversityView(APIView):
    permission_classes = (AllowAny,)
    # FIXME: only for test

    def get(self, request, format=None):
        cases = University.objects.all()
        serializer = UniversitySerializer(cases, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UniversitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SchoolView(APIView):
    permission_classes = (AllowAny,)
    # FIXME: only for test

    def get(self, request, format=None):
        cases = School.objects.all()
        serializer = SchoolSerializer(cases, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
