from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from course_database.models import ExperimentCaseDatabase
from experiment.models import CourseCase, ExperimentAssignment
from experiment.serializers import ExperimentCaseDatabaseSerializer, CourseCaseSerializer, ExperimentAssignmentSerializer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from experiment import utils
from course.models import Course, Teach
from user.models import TakeCourse
from user.serializers import TakeCourseSerializer

import datetime
import time


@api_view(['GET'])
@permission_classes([IsStudent | IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def student_get_case_detail(request, course_case_id):
    """
    get a course case detail info for student
    """
    try:
        course_case = CourseCase.objects.get(course_case_id=course_case_id)
    except CourseCase.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        course_case_serializer = CourseCaseSerializer(course_case)
        case_id = course_case_serializer['case_id']
        # 补充案例信息
        case = ExperimentCaseDatabase.objects.get(experiment_case_id=case_id.value)
        case_serializer = ExperimentCaseDatabaseSerializer(case)
        answer = dict(course_case_serializer.data)
        answer['experiment_name'] = case_serializer.data['experiment_name']
        answer['experiment_case_name'] = case_serializer.data['experiment_case_name']
        answer['experiment_case_description'] = case_serializer.data['experiment_case_description']
        # 补充提交信息
        try:
            answer['is_submit'] = True
            assignment = ExperimentAssignment.objects.get(course_case_id=course_case_id, submission_uploader=request.user.user_id)
            assignment_serializer = ExperimentAssignmentSerializer(assignment)
            answer['is_public_score'] = assignment_serializer.data['submission_is_public']
            answer['comment'] = assignment_serializer.data['submission_comments']
            answer['score'] = assignment_serializer.data['submission_score']
            answer['answer'] = assignment_serializer.data['submission_file_token']
        except ExperimentAssignment.DoesNotExist:
            answer['is_submit'] = False
        return Response(utils.generate_response(answer, True))


@api_view(['GET', 'POST'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def course_case_list(request, course_id):
    """
    List all cases of a specific course, or bind a case to this course.
    """
    if request.method == 'GET':
        cases = CourseCase.objects.all()
        cases = cases.filter(course_id=course_id)
        serializer = CourseCaseSerializer(cases, many=True)
        for index, case in enumerate(serializer.data):
            case_id = case['case_id']
            case_info = ExperimentCaseDatabase.objects.get(experiment_case_id=case_id)
            case_ser = ExperimentCaseDatabaseSerializer(case_info)
            serializer.data[index]['experiment_name'] = case_ser.data['experiment_name']
            serializer.data[index]['experiment_case_name'] = case_ser.data['experiment_case_name']
            serializer.data[index]['experiment_case_description'] = case_ser.data['experiment_case_description']
        ans = sorted(serializer.data, key=lambda x: datetime.datetime.strptime(x['case_start_timestamp'][:10], '%Y-%m-%d').timestamp())
        return Response(utils.generate_response(ans, True))

    elif request.method == 'POST':
        #  只有责任老师和老师才有创建的权限
        if request.user.character not in [1, 2]:
            error_msg = {"detail": "没有权限"}
            return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        elif request.user.character in [2]:
            try:
                print('*'*10, course_id, request.user.user_id, '*'*10)
                teach = Teach.objects.get(course_id=course_id, teacher_id=request.user.user_id)
            except Teach.DoesNotExist:
                error_msg = {"detail": "没有权限"}
                return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)

        serializer = CourseCaseSerializer(data=request.data)
        if serializer.is_valid():
            # 结束时间应该晚于开始时间
            start_time = request.data['case_start_timestamp'][:10]
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d').date()
            end_time = request.data['case_end_timestamp'][:10]
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d').date()
            if start_time >= end_time:
                error_msg = {"detail": "开始时间应早于结束时间，且不为同一天"}
                return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response(utils.generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def course_case_detail(request, pk):
    """
    Retrieve, update or delete a course case instance.
    """
    try:
        case = CourseCase.objects.get(pk=pk)
    except CourseCase.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CourseCaseSerializer(case)
        return Response(utils.generate_response(serializer.data, True))

    elif request.method == 'PUT':
        if request.user.character not in [1, 2]:
            error_msg = {"detail": "没有权限"}
            return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        elif request.user.character in [2]:
            try:
                print('*'*10, course_id, request.user.user_id, '*'*10)
                teach = Teach.objects.get(course_id=course_id, teacher_id=request.user.user_id)
            except Teach.DoesNotExist:
                error_msg = {"detail": "没有权限"}
                return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = CourseCaseSerializer(
            case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True))
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)
