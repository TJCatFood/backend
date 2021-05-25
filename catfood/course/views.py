from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from course.models import Course, Teach
from course.serializers import CourseSerializers, TeachSerializers
from rest_framework import generics
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import AllowAny
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from user.models import User
from course.utils import generate_response

from experiment import utils
from course.utils import is_student_within_course, is_teacher_teach_course
from user.models import TakeCourse
from user.serializers import TakeCourseSerializer
from django.core.exceptions import ObjectDoesNotExist

# add upload

import random
import os
import pandas as pd


@api_view(['GET'])
@permission_classes([IsStudent | IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def take_list(request):
    if request.method == 'GET':
        take_list = TakeCourse.objects.all()
        serializer = TakeCourseSerializer(take_list, many=True)
        answer = serializer.data
        for index, take in enumerate(answer):
            course_id = take['course_id']
            course_info = CourseSerializers(Course.objects.get(course_id=course_id)).data
            answer[index]['course_name'] = course_info['course_name']
            answer[index]['course_description'] = course_info['course_description']
            answer[index]['course_credit'] = course_info['course_credit']
            user_id = take['student_id']
            student = User.objects.get(pk=user_id)
            answer[index]['email'] = student.email
<<<<<<< HEAD
            answer[index]['realname'] = student.realname
            answer[index]['student_user_id'] = answer[index]['student_id']
            answer[index]['student_id'] = student.personal_id
=======
>>>>>>> ff53bc8cf725a5182e5df7be62b71e5cba11d1ff
        return Response(generate_response(serializer.data, True))


@api_view(['POST'])
@permission_classes([IsStudent | IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def upload(request):
    if request.method == "POST":
        # 检查是否存在文件表单
        try:
            excel_file = request.FILES['student-course-list-file']
        except Exception as e:
            print('in exception error is:', str(e))
            return Response({'is_success': False, 'msg': 'your form data lost key:'+str(e)}, status=status.HTTP_400_BAD_REQUEST)
        rd = str(int(random.random() * 1e6))
        tmp_file_name = rd + 'student-course-list.xlsx'
        response_msg = []

        # 是否成功导入
        try:
            # 读取数据到data frame
            with open(tmp_file_name, 'wb') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)
            df = pd.read_excel(tmp_file_name, engine='openpyxl')
            keys = df.keys()
            # 文件列名检查
            # 此处student_id是学号
            print(set(keys))
            if set(keys) == {'student_id', 'course_id'}:
                # 遍历检查合法性
                for index, row in df.iterrows():
                    row_dict = dict(row)
                    email = str(row_dict['student_id']) + '@tongji.edu.cn'
                    course_id = row_dict['course_id']
                    student = User.objects.filter(email=email)
                    # 检查学生
                    if len(student) == 0:
                        return Response({'is_success': False, 'msg': 'student:' + email + ' not exists'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    # 检查课程
                    try:
                        course = Course.objects.get(pk=course_id)
                    except Exception as e:
                        print(str(e))
                        return Response({'is_success': False, 'msg': 'course:' + str(course_id) + ' not exists'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    # 检查选课
                    try:
                        takeCourseItem = TakeCourse.objects.get(student_id=student[0].user_id, course_id=course)
                        return Response(
                            {'is_success': False, 'msg': email + 'take course:' + str(course_id) + 'exists'},
                            status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        pass
                # 遍历并且导入
                for index, row in df.iterrows():
                    row_dict = dict(row)
                    email = str(row_dict['student_id']) + '@tongji.edu.cn'
                    course_id = row_dict['course_id']
                    student = User.objects.filter(email=email)
                    user_id = student[0].user_id
                    serializer = TakeCourseSerializer(data={
                        'course_id': course_id,
                        'student_id': user_id
                    })
                    if serializer.is_valid():
                        serializer.save()
                return Response({'is_success': True}, status=status.HTTP_201_CREATED)

            elif set(keys) == {'email', 'course_id'}:
                # FIXME: 支持email导入
                e = 'in exception, error is: columns name is not: student_id, course_id or email, course_id'
                print(e)
                return Response({'is_success': False, 'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                e = 'in exception, error is: columns name is not: student_id, course_id or email, course_id'
                print(e)
                return Response({'is_success': False, 'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(str(e))
            is_success = False
            return Response({'is_success': False, 'msg': response_msg}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            os.remove(tmp_file_name)

# 11


@api_view(['GET', 'POST'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def courses_list(request):
    """
    List all courses, or create a new course.
    """
    if request.method == 'GET':
        user_id = request.user.user_id
        if request.user.character in [2, 3]:
            teaches_objects = Teach.objects.filter(teacher_id=user_id)
            teaches_list = TeachSerializers(teaches_objects, many=True).data
            course_list = []
            for teach in teaches_list:
                course = CourseSerializers(Course.objects.get(course_id=teach['course_id'])).data
                course_list.append(course)
        elif request.user.character == 1:
            course_list = CourseSerializers(Course.objects.all(), many=True).data
        else:
            # for student
            takes_list = TakeCourseSerializer(TakeCourse.objects.filter(student_id=user_id), many=True).data
            course_list = []
            for take in takes_list:
                course = CourseSerializers(Course.objects.get(course_id=take['course_id'])).data
                course_list.append(course)
        return Response(generate_response(course_list, True))

    elif request.method == 'POST':
        serializer = CourseSerializers(data=request.data)
        if request.user.character in [2, 3, 4]:
            response_data = {"error_msg": 'permission denied'}
            return Response(utils.generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def course_detail(request, course_id):
    """
    Retrieve or update a course instance.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        error_msg = {"detail": "object not exists"}
        return Response(generate_response(error_msg, False), status=status.HTTP_404_NOT_FOUND)

    user_id = request.user.user_id
    if request.user.character in [2, 3]:
        if not is_teacher_teach_course(teacher_id=user_id, course_id=course_id):
            response_data = {"error_msg": 'permission denied'}
            return Response(utils.generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)
    elif request.user.character == 4:
        if not is_student_within_course(student_id=user_id, course_id=course_id):
            response_data = {"error_msg": 'permission denied'}
            return Response(utils.generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        serializer = CourseSerializers(course)
        return Response(generate_response(serializer.data, True))

    elif request.method == 'PUT':
        teacher = User.objects.get(user_id=request.user.user_id)
        if teacher.character not in [1]:
            error_msg = {"detail": "没有权限"}
            return Response(generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = CourseSerializers(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True))
        return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if request.user.character in [1]:
            course.delete()
            response_data = {"detail": "have delete"}
            return Response(generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)
        else:
            error_msg = {"detail": "没有权限"}
            return Response(generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsChargingTeacher])
@authentication_classes([CatfoodAuthentication])
def teach_list(request):
    """
    List all teach relations, or create a new tech relation.
    """
    if request.method == 'GET':
        teach_list = Teach.objects.all()
        serializer = TeachSerializers(teach_list, many=True)
        answer = serializer.data
        for index, teach in enumerate(answer):
            course_id = teach['course_id']
            course_info = CourseSerializers(Course.objects.get(course_id=course_id)).data
            answer[index]['course_name'] = course_info['course_name']
            answer[index]['course_description'] = course_info['course_description']
            answer[index]['course_credit'] = course_info['course_credit']
        return Response(generate_response(serializer.data, True))

    elif request.method == 'POST':
        teacher_id = request.data['teacher_id']
        try:
            teacher = User.objects.get(user_id=teacher_id)
        except ObjectDoesNotExist:
            error_msg = {"detail": "被邀请人ID不存在"}
            return Response(generate_response(error_msg, False), status=status.HTTP_404_NOT_FOUND)
        teacher = User.objects.get(pk=teacher_id)
        if teacher.character not in [2, 3]:
            error_msg = {"detail": "被邀请人身份不符合要求"}
            return Response(generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = TeachSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsChargingTeacher])
@authentication_classes([CatfoodAuthentication])
def teach_detail(request, teach_id):
    """
    delete a teach relation.
    """
    try:
        teach = Teach.objects.get(pk=teach_id)
    except Teach.DoesNotExist:
        error_msg = {"detail": "object not exists"}
        return Response(generate_response(error_msg, False), status=status.HTTP_404_NOT_FOUND)

    teach.delete()
    msg = {"detail": "has been deleted successfully"}
    return Response(generate_response(msg, True), status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def get_students_by_course_id(request, course_id):
    """
    List all courses, or create a new course.
    """
    if request.method == 'GET':

        # check params
        params = request.query_params.dict()
        pg_num = params.get('pageNum', None)
        pg_size = params.get('pageSize', None)
        is_valid, error_response = utils.page_params_check(pg_num, pg_size)
        if not is_valid:
            return Response(utils.generate_response(error_response, False), status=status.HTTP_400_BAD_REQUEST)
        pg_num, pg_size = int(pg_num), int(pg_size)

        if request.user.character in [2, 3]:
            teacher_id = request.user.user_id
            teaches = Teach.objects.filter(teacher_id=teacher_id)
            teaches_serializer = TeachSerializers(teaches, many=True)
            course_id_list = []
            for teach in teaches_serializer.data:
                course_id_list.append(teach['course_id'])
            if course_id not in course_id_list:
                response_data = {
                    "error_msg": 'permission denied, You have not yet bound the corresponding course'
                }
                return Response(utils.generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)
        take_objects = TakeCourse.objects.filter(course_id=course_id)
        take_list = TakeCourseSerializer(take_objects, many=True).data
        student_list = []
        for take in take_list:
            student_object = User.objects.get(user_id=take['student_id'])
            student_list.append(utils.my_user_serializer(student_object))
        sorted(student_list, key=lambda x: x['user_id'])
        pg_end = min(pg_num*pg_size, len(student_list))
        pg_start = (pg_num-1)*pg_size
        if pg_start < len(student_list):
            response_student_list = student_list[pg_start:pg_end]
        else:
            response_student_list = []
        ans = {
            'students': response_student_list,
            'pagination': {
                'pageNum': pg_num,
                'pageSize': pg_size,
                'total': len(student_list)
            }
        }
        return Response(ans)
