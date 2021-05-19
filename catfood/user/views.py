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
from .models import User, University, School, TakeCourse
from .serializers import UniversitySerializer, SchoolSerializer, TakeCourseSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from course.models import Course

from django import forms
from django.http import HttpResponseBadRequest
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from experiment.utils import my_user_serializer
import pandas as pd
import io
import os
from django import forms
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from django.core.cache import cache


class PasswordRestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        try:
            receiver = request.data['email']
        except Exception as e:
            print(str(e))
            return Response({"is_success": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        sender = 'tongjicatfood@163.com'
        token = int(random.random()*1e6)
        message = MIMEText('找回密码token:' + str(token), 'plain', 'utf-8')
        message['From'] = "TongjiCatfood<tongjicatfood@163.com>"
        message['To'] = 'receivers<' + sender + '>'
        subject = '找回密码'
        message['Subject'] = subject
        receivers = [receiver]
        try:
            smtpObj = smtplib.SMTP(host='smtp.163.com', port=25)
            # 包含密钥 不要泄露
            smtpObj.login("tongjicatfood@163.com", "BGZVPKDGAFEXCHCT")
            print("S")
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("S")
        except smtplib.SMTPException as a:
            print(a)
            print("F")
            return Response({"is_success": False, "msg": str(a)}, status=status.HTTP_400_BAD_REQUEST)

        cache.set(receiver, token, timeout=2500)
        return Response({"is_success": True}, status=status.HTTP_200_OK)


class PwdResetTokenVerify(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        try:
            email = request.data['email']
            token = request.data['token']
            new_password = request.data['new_password']
            print(token, cache.get(email))
            if int(token) == int(cache.get(email)):
                try:
                    print('skip')
                    # print('will get users', email)
                    # print('all:', User.objects.all())
                    # user = User.objects.filter(email=email)
                    # print(user)
                    # print('get user:', user)
                    # user.set_password(new_password)
                    # print('set pwd finish')
                    # user.save()
                    # print('save finish')
                    cache.set('new_pwd/'+email, new_password, timeout=None)
                    return Response({"is_success": True}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response(
                        {
                            "is_success": False,
                            "msg": "user not exists:" + str(e)
                        },
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"is_success": False, "msg": "token verify failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"is_success": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsStudent | IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def upload(request):
    if request.method == "POST":
        try:
            excel_file = request.FILES['student-list-file']
        except Exception as e:
            print('in exception error is:', str(e))
            return Response({'is_success': False, 'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        rd = str(int(random.random() * 1e6))
        tmp_file_name = rd + 'student-list.xlsx'
        response_msg = []
        is_success = True
        try:
            with open(tmp_file_name, 'wb') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)
            df = pd.read_excel(tmp_file_name, engine='openpyxl')
            for index, row in df.iterrows():
                try:
                    row_dict = dict(row)
                    password = row_dict['password']
                    realname = row_dict['realname']
                    university_id = row_dict['university_id']
                    school_id = row_dict['school_id']
                    character = row_dict['character']
                    personal_id = row_dict['personal_id']
                    email = row_dict['email']
                    user = User.objects.create(password=password, realname=realname,
                                               email=email, university_id=university_id, school_id=school_id,
                                               character=character,
                                               personal_id=personal_id, avatar=None)
                except Exception as e:
                    is_success = False
                    msg = str(index) + "row error" + str(e)
                    msg = msg.split('DETAIL:')[1].strip()
                    response_msg.append(msg)
        except Exception as e:
            is_success = False
            return Response({'is_success': is_success, 'msg': response_msg}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            os.remove(tmp_file_name)

        # tmp = excel_file.get_sheet()
        # print(tmp)
        if is_success:
            return Response({'is_success': is_success}, status=status.HTTP_201_CREATED)
        else:
            return Response({'is_success': is_success, 'msg': response_msg}, status=status.HTTP_400_BAD_REQUEST)

        # return excel.make_response(excel_file.get_sheet(), "csv")

        # print(request.Post.get('file'))

        # if form.is_valid():
        #     filehandle = request.FILES['test_file']
        #     print("file handle:", filehandle)
        #     return excel.make_response(filehandle.get_sheet(), "csv")
        # else:
        #     return HttpResponseBadRequest()


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        # use email
        try:
            email = request.data['email']

            ct_user = my_user_serializer(User.objects.filter(email=email)[0])
        except Exception as e:
            print(str(e))
            return Response({"is_success": False, "error_msg": "parameters error"}, status=status.HTTP_400_BAD_REQUEST)
        # login with session_id
        if request.session.get(ct_user['user_id']):
            user_id = request.session['user_id']
            user = User.objects.get(user_id=user_id)
            if request.session.get("password") == user.password:
                content = {
                    'isSuccess': True,
                    'data': {
                        'user_id': user.user_id,
                        'realname': user.realname,
                        'email': user.email,
                        'university_name': user.university_id.university_name,
                        'school_name': user.school_id.school_name,
                        'character': user.character,
                        'personal_id': user.personal_id,
                        'avatar': user.avatar,
                    }
                }
                return Response(content)

        # login with user_id and password
        try:
            user_id = ct_user['user_id']
        except(MultiValueDictKeyError):
            user_id = None
        except Exception as e:
            user_id = None
        try:
            new_password = cache.get("new_pwd/"+email)
            if new_password is not None:
                try:
                    user = User.objects.get(pk=user_id)
                except(ObjectDoesNotExist):
                    content = {
                        'isSuccess': False,
                        'error': {
                            'message': "输入的用户ID不存在"
                        }
                    }
                    return Response(content, status=400)
                user.set_password(new_password)
                print('set new password')
                user.save()
                print('save new password')
                password = new_password
            else:
                password = request.data['password']
        except(MultiValueDictKeyError):
            password = None
        except Exception as e:
            password = None
        # check the user_id
        try:
            user = User.objects.get(pk=user_id)
        except(ObjectDoesNotExist):
            content = {
                'isSuccess': False,
                'error': {
                    'message': "输入的用户ID不存在"
                }
            }
            return Response(content, status=400)
        except Exception as e:
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
                'user_id': user.user_id,
                'realname': user.realname,
                'email': user.email,
                'university_name': user.university_id.university_name,
                'school_name': user.school_id.school_name,
                'character': user.character,
                'personal_id': user.personal_id,
                'avatar': user.avatar,
            }
        }
        request.session['user_id'] = user.user_id
        request.session['password'] = user.password
        request.session["login"] = True
        return Response(content)


class LogoutView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def post(self, request):
        try:
            del request.session['login']
            del request.session['user_id']
        except KeyError:
            pass
        request.session.flush()
        content = {
            'isSuccess': True,
            'data': {
                'message': "登出成功"
            }
        }
        return Response(content)


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
            email = request.data["email"]
        except Exception as e:
            print(str(e))
            content = {
                'isSuccess': False,
                'error': {
                    'message': str(e)
                }
            }
            return Response(content, status=400)

        try:
            avatar = request.data["avatar"]
        except MultiValueDictKeyError:
            avatar = None
        except Exception as e:
            print(str(e))
            avatar = None

        try:
            user = User.objects.create(password=password, realname=realname,
                                       email=email, university_id=university_id, school_id=school_id, character=character,
                                       personal_id=personal_id, avatar=avatar)
        except Exception as e:
            print(e)
            content = {
                'isSuccess': False,
                'error': {
                    'message': str(e)
                }
            }
            return Response(content, status=400)

        request.session.flush()
        content = {
            'isSuccess': True,
            'data': {
                'user_id': user.user_id,
                'realname': user.realname,
                'email': user.email,
                'university_name': user.university_id.university_name,
                'school_name': user.school_id.school_name,
                'character': user.character,
                'personal_id': user.personal_id,
                'avatar': user.avatar,
            }
        }
        return Response(content, status=201)


class AccountView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, format=None):
        user = request.user
        content = {
            'isSuccess': True,
            'data': {
                'user_id': user.user_id,
                'realname': user.realname,
                'email': user.email,
                'university_name': user.university_id.university_name,
                'school_name': user.school_id.school_name,
                'character': user.character,
                'personal_id': user.personal_id,
                'avatar': user.avatar,
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
        content = {
            'isSuccess': True,
            'data': {
                'user_id': user.user_id,
                'realname': user.realname,
                'email': user.email,
                'university_name': user.university_id.university_name,
                'school_name': user.school_id.school_name,
                'character': user.character,
                'personal_id': user.personal_id,
                'avatar': user.avatar,
            }
        }
        return Response(content, status=200)


class PasswordView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

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
            return Response(content, status=200)
        try:
            password = request.data["password"]
        except(MultiValueDictKeyError):
            password = None
        user.set_password(password)
        user.save()
        request.session.flush()
        content = {
            'isSuccess': True,
            'data': {
                'message': '密码更改成功'
            }
        }
        return Response(content, status=200)


class AccountsView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsChargingTeacher]

    def post(self, request, format=None):
        for student in request.data:
            try:
                password = student['password']
                realname = student['realname']
                university_id = student['university_id']
                school_id = student['school_id']
                character = student['character']
                personal_id = student['personal_id']
            except(KeyError):
                content = {
                    'isSuccess': False,
                    'error': {
                        'message': "待导入学生缺少必需信息"
                    }
                }
                return Response(content, status=200)
            try:
                avatar = student["avatar"]
            except(KeyError):
                avatar = None
            try:
                email = student["email"]
            except(KeyError):
                email = None

            try:
                university = University.objects.get(university_id=university_id)
                school = School.objects.get(school_id=school_id)
                user = User(
                    realname=realname,
                    email=User.objects.normalize_email(email),
                    university_id=university,
                    school_id=school,
                    personal_id=personal_id,
                    character=character,
                    avatar=avatar,
                )
            except(Exception):
                content = {
                    'isSuccess': False,
                    'error': {
                        'message': "字段违反数据库约束（如外码约束和长度约束）"
                    }
                }
                return Response(content, status=400)

        responseData = []
        for student in request.data:
            user = User.objects.create(password=password, realname=realname,
                                       email=email, university_id=university_id, school_id=school_id, character=character,
                                       personal_id=personal_id, avatar=avatar)
            responseData.append({"user_id": user.user_id, 'realname': user.realname, 'email': user.email,
                                 'university_name': user.university_id.university_name,
                                 'school_name': user.school_id.school_name, 'character': user.character,
                                 'personal_id': user.personal_id, 'avatar': user.avatar})

        content = {
            'isSuccess': True,
            'data': responseData,
        }
        return Response(content, status=status.HTTP_201_CREATED)


class CoursesView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsChargingTeacher]

    def post(self, request, format=None):
        for takeCourse in request.data:
            try:
                student_id = takeCourse["student_id"]
                course_id = takeCourse["course_id"]
            except(KeyError, TypeError):
                content = {
                    'isSuccess': False,
                    'error': {
                        'message': "缺少用户号或课号"
                    }
                }
                return Response(content, status=200)
            try:
                student = User.objects.get(user_id=student_id)
                course = Course.objects.get(course_id=course_id)
            except(ObjectDoesNotExist):
                content = {
                    'isSuccess': False,
                    'error': {
                        'message': "用户号或课号不满足外码约束"
                    }
                }
                return Response(content, status=200)
            try:
                takeCourseItem = TakeCourse.objects.get(student_id=student, course_id=course)
            except(ObjectDoesNotExist):
                serializer = TakeCourseSerializer(data=takeCourse)
            else:
                serializer = TakeCourseSerializer(takeCourseItem, data=takeCourse)
            if not serializer.is_valid():
                content = {
                    'isSuccess': False,
                    'error': {
                        'message': "选课情况解析失败"
                    }
                }
                return Response(content, status=200)

        for takeCourse in request.data:
            student = User.objects.get(user_id=student_id)
            course = Course.objects.get(course_id=course_id)
            try:
                takeCourseItem = TakeCourse.objects.get(student_id=student, course_id=course)
            except(ObjectDoesNotExist):
                serializer = TakeCourseSerializer(data=takeCourse)
            else:
                serializer = TakeCourseSerializer(takeCourseItem, data=takeCourse)
            if serializer.is_valid():
                serializer.save()

        content = {
            'isSuccess': True,
            'data': {
                'message': '选课情况导入成功'
            }
        }
        return Response(content, status=status.HTTP_201_CREATED)


class UniversityView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        cases = University.objects.all()
        serializer = UniversitySerializer(cases, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # FIXME: only for test
        serializer = UniversitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SchoolView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        cases = School.objects.all()
        serializer = SchoolSerializer(cases, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # FIXME: only for test
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
