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


@api_view(['GET', 'POST'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def courses_list(request):
    """
    List all courses, or create a new course.
    """
    if request.method == 'GET':
        if request.user.character in [2, 3]:
            teacher_id = request.user.user_id
            teachs = Teach.objects.all()
            teachs_serializer = TeachSerializers(teachs.filter(teacher_id=teacher_id), many=True)
            answer = []
            for teach in teachs_serializer.data:
                course_id = teach['course_id']
                courses = Course.objects.all()
                courses_serializer = CourseSerializers(courses.filter(course_id=course_id), many=True)
                answer.extend(courses_serializer.data)
            return Response(generate_response(answer, True))
        elif request.user.character in [4]:
            pass
        courses = Course.objects.all()
        serializer = CourseSerializers(courses, many=True)
        print(serializer.data)
        return Response(generate_response(serializer.data, True))

    elif request.method == 'POST':
        teacher = User.objects.get(user_id=request.user.user_id)
        if teacher.character not in [1]:
            error_msg = {"detail": "没有权限"}
            return Response(generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = CourseSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


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
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant])
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
        teacher = User.objects.get(user_id=request.user.user_id)
        if teacher.character not in [1]:
            error_msg = {"detail": "邀请人没有权限"}
            return Response(generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        if teacher.character not in [1, 2, 3]:
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
