from django.shortcuts import render
from django.contrib import auth
from django.db.models import Max
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
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        # login with session_id
        if request.session.get("user_id"):
            user_id = request.session['user_id']
            user = User.objects.get(user_id=user_id)
            if request.session.get("password") == user.password:
                content = {
                    'isSuccess': True,
                    'data': {
                        'user_id': f"{user.user_id}",
                        'realname': f"{user.realname}",
                        'email': f"{user.email}",
                        'university_name': f"{user.university_id.university_name}",
                        'school_name': f"{user.school_id.school_name}",
                        'character': f"{user.character}",
                        'personal_id': f"{user.personal_id}",
                        'avatar': f"{user.avatar}",
                    }
                }
                return Response(content)

        # login with user_id and password
        try:
            user_id = request.data["user_id"]
        except(MultiValueDictKeyError):
            user_id = None
        try:
            password = request.data["password"]
        except(MultiValueDictKeyError):
            password = None
        # check the user_id
        try:
            user = User.objects.get(user_id=user_id)
        except(ObjectDoesNotExist):
            content = {
                'isSuccess': False,
                'error': {
                    'message': "输入的用户ID不存在"
                }
            }
            return Response(content, status=400)

        # check the password
        if not user.check_password(password):
            content = {
                'isSuccess': False,
                'error': {
                    'message': "用户ID与密码不匹配"
                }
            }
            return Response(content, status=400)

        content = {
            'isSuccess': True,
            'data': {
                'user_id': f"{user.user_id}",
                'realname': f"{user.realname}",
                'email': f"{user.email}",
                'university_name': f"{user.university_id.university_name}",
                'school_name': f"{user.school_id.school_name}",
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
            'isSuccess': True,
            'date': {
                'message': "登出成功"
            }
        }
        return Response(content, status=201)


class RegisterView(APIView):
    # FIXME: remove student registration and add invitation codes
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        try:
            password = request.data['password']
            realname = request.data['realname']
            university_id = request.data['university_id']
            school_id = request.data['school_id']
            character = request.data['character']
            personal_id = request.data['personal_id']
        except(MultiValueDictKeyError):
            content = {
                'isSuccess': False,
                'data': {
                    'message': "缺少必填信息"
                }
            }
            return Response(content, status=400)

        try:
            avatar = request.data["avatar"]
        except(MultiValueDictKeyError):
            avatar = None
        try:
            email = request.data["email"]
        except(MultiValueDictKeyError):
            email = None

        try:
            user = User.objects.create(password=password, realname=realname,
                                       email=email, university_id=university_id, school_id=school_id, character=character,
                                       personal_id=personal_id, avatar=avatar)
        except(ObjectDoesNotExist):
            content = {
                'isSuccess': False,
                'error': {
                    'message': "大学或学院编号不符合外码约束"
                }
            }
            return Response(content, status=400)
        request.session.flush()
        content = {
            'isSuccess': True,
            'data': {
                'user_id': f"{user.user_id}",
                'realname': f"{user.realname}",
                'email': f"{user.email}",
                'university_name': f"{user.university_id.university_name}",
                'school_name': f"{user.school_id.school_name}",
                'character': f"{user.character}",
                'personal_id': f"{user.personal_id}",
                'avatar': f"{user.avatar}",
            }
        }
        return Response(content, status=201)


class AccountView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, format=None):
        user = request.user
        content = {
            'isSuccess': True,
            'data': {
                'user_id': f"{user.user_id}",
                'realname': f"{user.realname}",
                'email': f"{user.email}",
                'university_name': f"{user.university_id.university_name}",
                'school_name': f"{user.school_id.school_name}",
                'character': f"{user.character}",
                'personal_id': f"{user.personal_id}",
                'avatar': f"{user.avatar}",
            }
        }
        return Response(content)

    def patch(self, request, format=None):
        user = request.user
        try:
            email = request.data["email"]
        except(MultiValueDictKeyError):
            email = None
        try:
            avatar = request.data["avatar"]
        except(MultiValueDictKeyError):
            avatar = None
        if email:
            user.email = User.objects.normalize_email(email)
        if avatar:
            user.avatar = avatar
        user.save()
        isSuccess = 'true'
        content = {
            'isSuccess': f"{isSuccess}",
            'data': {
                'user_id': f"{user.user_id}",
                'realname': f"{user.realname}",
                'email': f"{user.email}",
                'university_name': f"{user.university_id.university_name}",
                'school_name': f"{user.school_id.school_name}",
                'character': f"{user.character}",
                'personal_id': f"{user.personal_id}",
                'avatar': f"{user.avatar}",
            }
        }
        return Response(content, status=200)


class PasswordView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def patch(self, request, format=None):
        user = request.user
        try:
            old_password = request.data["old_password"]
        except(MultiValueDictKeyError):
            old_password = None
        if not user.check_password(old_password):
            content = {
                'isSuccess': False,
                'error': {
                    'message': "旧密码错误"
                }
            }
            return Response(content, status=400)
        try:
            password = request.data["password"]
        except(MultiValueDictKeyError):
            password = None
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
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsChargingTeacher]

    def post(self, request, format=None):
        content = {
            'isSuccess': 'true',
            'data': {
                'message': '账户导入成功'
            }
        }
        return Response(content, status=status.HTTP_201_CREATED)


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
