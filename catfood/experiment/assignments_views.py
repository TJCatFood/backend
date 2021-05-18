from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from course_database.models import ExperimentCaseDatabase
from experiment.models import CourseCase, ExperimentAssignment
from user.models import TakeCourse
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
from course.serializers import TeachSerializers

import datetime
import random

from minio import Minio
from minio.error import ResponseError
from datetime import timedelta
from os import environ

from catfood.settings import MINIO_STORAGE_MEDIA_BUCKET_NAME as DEFAULT_BUCKET
from catfood.settings import MINIO_STORAGE_USE_HTTPS

# minio client to use
local_minio_client = Minio(
    environ['MINIO_ADDRESS'],
    access_key=environ['MINIO_ACCESS_KEY'],
    secret_key=environ['MINIO_SECRET_KEY'],
    secure=MINIO_STORAGE_USE_HTTPS,
)

# default file URL timeout = 15 min
DEFAULT_FILE_URL_TIMEOUT = timedelta(minutes=15)

# COURSE_DOCUMENT_BUCKET

EXPERIMENT_CASE_PREFIX = "experiment_case"


@api_view(['PUT'])
@permission_classes([IsChargingTeacher])
@authentication_classes([CatfoodAuthentication])
def teacher_public_all_assignments(request, course_case_id):
    if request.method == 'PUT':
        assignment_model_list = ExperimentAssignment.objects.all().filter(course_case_id=course_case_id)
        assignment_list = ExperimentAssignmentSerializer(assignment_model_list, many=True)
        for index, assignment in enumerate(assignment_list.data):
            change_data = assignment
            change_data['submission_is_public'] = True
            print(change_data)
            assignment_serializer = ExperimentAssignmentSerializer(assignment_model_list[index], data=change_data, partial=True)
            if assignment_serializer.is_valid():
                assignment_serializer.save()
            else:
                print(assignment_serializer.errors)
                error_data = {"detail": "update error"}
                return Response(utils.generate_response(error_data, False))
        success_data = {"detail": "success"}
        return Response(utils.generate_response(success_data, True), status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsStudent])
@authentication_classes([CatfoodAuthentication])
def assignment_student_list(request):
    """
    List all assignments for a particular student.
    Submit a assignment
    """
    if request.method == 'GET':
        assignments = ExperimentAssignment.objects.filter(submission_uploader=request.user.user_id)
        # assignments = assignments.filter()
        serializer = ExperimentAssignmentSerializer(assignments, many=True)
        return Response(utils.generate_response(utils.student_assignments_filter(serializer.data), True))

    elif request.method == 'POST':
        # 输入字段检测
        if not utils.is_submission_valid(request.data):
            return Response(utils.generate_response({"error_msg": '参数错误'}, False), status=status.HTTP_400_BAD_REQUEST)

        # 获取学生选过的课程集合
        user_id = request.user.user_id
        course_objects = TakeCourse.objects.filter(student_id=user_id)
        course_id_list = []
        tmp_serializer = TakeCourseSerializer(course_objects, many=True)

        for item in tmp_serializer.data:
            course_id_list.append(item['course_id'])
        course_id_set = set(course_id_list)

        # 检测上传的课程是否是在选过的课程中
        course_id = request.data['course_id']
        if course_id not in course_id_set:
            error_res = {"error_msg": '提交的课程尚未加入'}
            return Response(utils.generate_response(error_res, False), status=status.HTTP_400_BAD_REQUEST)
        print('wzj')
        try:
            course_case_object = CourseCase.objects.get(pk=request.data['course_case_id'])
        except CourseCase.DoesNotExist:
            error_data = {"detail": "course case not exist"}
            return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

        course_case = CourseCaseSerializer(course_case_object).data

        # DDL检验
        if not utils.check_ddl(course_case['case_end_timestamp']):
            return Response(utils.generate_response({"error_msg": 'Assignment is due'}, False))

        request.data['submission_uploader'] = user_id

        # upload url
        response_headers = {}
        file_display_name = request.data["submission_file_name"]
        random_hex_string = ('%030x' % random.randrange(16 ** 30))
        file_token = f"{EXPERIMENT_CASE_PREFIX}/{random_hex_string}/{file_display_name}"
        post_url = local_minio_client.presigned_url("PUT",
                                                    DEFAULT_BUCKET,
                                                    file_token,
                                                    expires=DEFAULT_FILE_URL_TIMEOUT)
        request.data['submission_file_token'] = file_token
        response_headers['SUBMISSION_UPLOAD_URL'] = post_url

        serializer = ExperimentAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True), headers=response_headers, status=status.HTTP_201_CREATED)
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def assignment_student_detail(request, pk):
    """
    Retrieve, update or delete a assignment submission instance.
    """
    try:
        assignment = ExperimentAssignment.objects.get(pk=pk)
    except ExperimentAssignment.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        serializer = ExperimentAssignmentSerializer(assignment)

        # 生成 minio 下载 url
        response_headers = {}
        file_token = serializer.data['submission_file_token']
        get_url = local_minio_client.presigned_url("GET",
                                                   DEFAULT_BUCKET,
                                                   file_token,
                                                   expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers['ASSIGNMENT_DOWNLOAD_URL'] = get_url

        ans = serializer.data
        ans.pop('submission_file_token', None)
        return Response(utils.generate_response(utils.student_assignments_filter([ans])[0], True), headers=response_headers)

    elif request.method == 'PUT':
        old_assignment = ExperimentAssignmentSerializer(assignment).data
        # Public检验
        if not utils.is_submission_retrieve_valid(old_assignment, request.data):
            return Response(utils.generate_response({"error_msg": 'permission denied'}, False), status=status.HTTP_400_BAD_REQUEST)

        # DDL检验
        course_case_object = CourseCase.objects.get(course_case_id=old_assignment['course_case_id'])
        course_case = CourseCaseSerializer(course_case_object).data
        if not utils.check_ddl(course_case['case_end_timestamp']):
            return Response(utils.generate_response({"error_msg": 'Assignment is due'}, False))

        # upload url
        response_headers = {}
        file_token = old_assignment['submission_file_token']
        post_url = local_minio_client.presigned_url("PUT",
                                                    DEFAULT_BUCKET,
                                                    file_token,
                                                    expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers['SUBMISSION_UPLOAD_URL'] = post_url

        serializer = ExperimentAssignmentSerializer(
            assignment, data=old_assignment, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True), headers=response_headers)
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not utils.is_submission_delete_valid(
                ExperimentAssignmentSerializer(assignment).data):
            response_data = {"error_msg": 'permission denied'}
            return Response(utils.generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)
        assignment.delete()
        response_data = {"detail": "have delete"}
        return Response(utils.generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def assignment_teacher_list(request, course_case_id):
    """
    List all the assignments with a specific course_case_id for teacher.
    """
    if request.method == 'GET':
        assignments = ExperimentAssignment.objects.all()
        # TODO: 鉴权

        assignments = assignments.filter(course_case_id=course_case_id)
        serializer = ExperimentAssignmentSerializer(assignments, many=True)
        return Response(utils.generate_response(serializer.data, True))


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def assignment_teacher_detail(request, pk):
    """
    Retrieve, update or delete a assignment submission instance.
    """
    try:
        assignment = ExperimentAssignment.objects.get(pk=pk)
    except ExperimentAssignment.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentAssignmentSerializer(assignment)
        return Response(utils.generate_response(serializer.data, True))

    elif request.method == 'PUT':

        course_case_id = ExperimentAssignmentSerializer(assignment).data['course_case_id']
        course_object = CourseCase.objects.get(pk=course_case_id)
        course_id = CourseCaseSerializer(course_object).data['course_id']
        if request.user.character in [2, 3]:
            user_id = request.user.user_id
            # 检查是否绑定授课
            courses_set = set()
            teach_objects = Teach.objects.filter(teacher_id=user_id)
            teach_list = TeachSerializers(teach_objects, many=True)
            for teach in teach_list.data:
                courses_set.add(teach['course_id'])
            if course_id not in courses_set:
                response_data = {
                    "error_msg": 'permission denied, You have not yet bound the corresponding course'
                }
                return Response(utils.generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)
        selected_attributions = [
            'submission_case_id',
            'submission_score',
            'submission_is_public',
            'submission_comments'
        ]
        update_data = {item: request.data[item] for item in selected_attributions}
        # 非责任教师不允许public
        if request.user.character in [2, 3]:
            update_data.pop('submission_is_public')
        serializer = ExperimentAssignmentSerializer(
            assignment, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True))
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        assignment.delete()
        response_data = {"detail": "have delete"}
        return Response(utils.generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant])
@authentication_classes([CatfoodAuthentication])
def teacher_get_assignment_detail(request, submission_id):
    try:
        print('hello')
        assignment = ExperimentAssignment.objects.get(submission_case_id=submission_id)
    except ExperimentAssignment.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        assignment_serializer = ExperimentAssignmentSerializer(assignment)
        answer = dict(assignment_serializer.data)
        case_id = answer['submission_case_id']
        case = ExperimentCaseDatabase.objects.get(experiment_case_id=case_id)
        case_serializer = ExperimentCaseDatabaseSerializer(case)
        answer['experiment_name'] = case_serializer.data['experiment_name']
        answer['experiment_case_name'] = case_serializer.data['experiment_case_name']
        answer['experiment_case_description'] = case_serializer.data['experiment_case_description']

        # 生成 minio 下载 url
        response_headers = {}
        file_token = assignment_serializer.data['submission_file_token']
        get_url = local_minio_client.presigned_url("GET",
                                                   DEFAULT_BUCKET,
                                                   file_token,
                                                   expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers['ASSIGNMENT_DOWNLOAD_URL'] = get_url

        ans = assignment_serializer.data
        ans.pop('submission_file_token', None)

        return Response(utils.generate_response(answer, True), headers=response_headers)
