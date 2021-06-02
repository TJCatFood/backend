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

import json
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


@api_view(['GET', 'POST'])
@permission_classes([IsChargingTeacher | IsTeacher])
@authentication_classes([CatfoodAuthentication])
def experiment_case_list(request):
    """
    List all cases, or create a new case.
    """

    if request.method == 'GET':
        cases = ExperimentCaseDatabase.objects.all()
        serializer = ExperimentCaseDatabaseSerializer(cases, many=True)
        for index, case in enumerate(serializer.data):
            serializer.data[index].pop('experiment_case_file_token', None)
            serializer.data[index].pop('answer_file_token', None)
        ans = sorted(serializer.data, key=lambda x: datetime.datetime.strptime(x['case_created_timestamp'][:10], '%Y-%m-%d').timestamp())
        return Response(utils.generate_response(ans, True))
    elif request.method == 'POST':

        if not local_minio_client.bucket_exists(DEFAULT_BUCKET):
            local_minio_client.make_bucket(DEFAULT_BUCKET)

        new_case = {}
        response_headers = {}

        try:

            # case file
            file_display_name = request.data["experiment_case_file_name"]
            random_hex_string = ('%030x' % random.randrange(16 ** 30))
            file_token = f"{EXPERIMENT_CASE_PREFIX }/{random_hex_string}/{file_display_name}"
            post_url = local_minio_client.presigned_url("PUT",
                                                        DEFAULT_BUCKET,
                                                        file_token,
                                                        expires=DEFAULT_FILE_URL_TIMEOUT)
            new_case['experiment_case_file_token'] = file_token
            response_headers['CASE_FILE_UPLOAD_URL'] = post_url

            # answer file
            file_display_name = request.data["answer_file_name"]
            random_hex_string = ('%030x' % random.randrange(16 ** 30))
            file_token = f"{EXPERIMENT_CASE_PREFIX }/{random_hex_string}/{file_display_name}"
            post_url = local_minio_client.presigned_url("PUT",
                                                        DEFAULT_BUCKET,
                                                        file_token,
                                                        expires=DEFAULT_FILE_URL_TIMEOUT)
            new_case['answer_file_token'] = file_token
            response_headers['ANSWER_FILE_UPLOAD_URL'] = post_url

            # other info
            new_case['experiment_name'] = request.data['experiment_name']
            new_case['experiment_case_name'] = request.data['experiment_case_name']

        except Exception as e:
            print(str(e))
            return Response(utils.generate_response(str(e), False), status=status.HTTP_400_BAD_REQUEST)

        serializer = ExperimentCaseDatabaseSerializer(data=new_case)
        if serializer.is_valid():
            serializer.save()
            ans = serializer.data
            ans.pop('experiment_case_file_token', None)
            ans.pop('answer_file_token', None)
            return Response(utils.generate_response(ans, True), headers=response_headers, status=status.HTTP_201_CREATED)
        else:
            return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsChargingTeacher | IsTeacher])
@authentication_classes([CatfoodAuthentication])
def experiment_case_detail(request, pk):
    """
    Retrieve, update or delete a experiment case instance.
    """
    try:
        case = ExperimentCaseDatabase.objects.get(pk=pk)
    except ExperimentCaseDatabase.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentCaseDatabaseSerializer(case)
        # 生成 minio 下载 url
        response_headers = {}
        file_token = serializer.data['experiment_case_file_token']
        get_url = local_minio_client.presigned_url("GET",
                                                   DEFAULT_BUCKET,
                                                   file_token,
                                                   expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers['CASE_FILE_DOWNLOAD_URL'] = get_url
        file_token = serializer.data['answer_file_token']
        get_url = local_minio_client.presigned_url("GET",
                                                   DEFAULT_BUCKET,
                                                   file_token,
                                                   expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers['ANSWER_FILE_DOWNLOAD_URL'] = get_url
        # 去掉数据库中的 token 信息
        ans = serializer.data
        ans.pop('experiment_case_file_token', None)
        ans.pop('answer_file_token', None)
        return Response(utils.generate_response(ans, True), headers=response_headers)

    elif request.method == 'PUT':
        serializer = ExperimentCaseDatabaseSerializer(
            case, data=request.data, partial=True)
        if serializer.is_valid():

            response_headers = {}

            # case file
            file_display_name = serializer.data["experiment_case_file_name"]
            random_hex_string = ('%030x' % random.randrange(16 ** 30))
            file_token = f"{EXPERIMENT_CASE_PREFIX}/{random_hex_string}/{file_display_name}"
            post_url = local_minio_client.presigned_url("PUT",
                                                        DEFAULT_BUCKET,
                                                        file_token,
                                                        expires=DEFAULT_FILE_URL_TIMEOUT)
            response_headers['CASE_FILE_UPLOAD_URL'] = post_url

            # answer file
            file_display_name = serializer.data["answer_file_name"]
            random_hex_string = ('%030x' % random.randrange(16 ** 30))
            file_token = f"{EXPERIMENT_CASE_PREFIX}/{random_hex_string}/{file_display_name}"
            post_url = local_minio_client.presigned_url("PUT",
                                                        DEFAULT_BUCKET,
                                                        file_token,
                                                        expires=DEFAULT_FILE_URL_TIMEOUT)
            response_headers['ANSWER_FILE_UPLOAD_URL'] = post_url

            serializer.save()
            ans = serializer.data
            ans.pop('experiment_case_file_token', None)
            ans.pop('answer_file_token', None)
            return Response(utils.generate_response(ans, True), headers=response_headers)
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)
