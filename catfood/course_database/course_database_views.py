from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.db import models

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view

from rest_framework.permissions import AllowAny

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import CourseDocument
from .serializers import CourseDocumentSerializer

from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from course.utils import is_student_within_course, is_teacher_teach_course

from typing import Union

import json
import datetime
from enum import IntEnum

from minio import Minio
from minio.error import ResponseError
from datetime import timedelta
from os import environ

from catfood.settings import MINIO_STORAGE_MEDIA_BUCKET_NAME as DEFAULT_BUCKET
from catfood.settings import MINIO_STORAGE_USE_HTTPS

import random


local_minio_client = Minio(
    environ['MINIO_ADDRESS'],
    access_key=environ['MINIO_ACCESS_KEY'],
    secret_key=environ['MINIO_SECRET_KEY'],
    secure=MINIO_STORAGE_USE_HTTPS,
)

# default file URL timeout = 15 min
DEFAULT_FILE_URL_TIMEOUT = timedelta(minutes=15)

# placeholder for new file
MINIO_FILE_PLACEHOLDER = b"THIS IS A PLACEHOLDER FOR NEW FILE"

# COURSE_DOCUMENT_BUCKET

COURSE_DOCUMENT_PREFIX = "course_document"

# Course file database starts


class CourseView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        query_dict = request.query_params
        need_pagination = False
        pagination_page_size = -1
        pagination_page_num = -1

        if query_dict:
            # find out whether the user requested for pagination
            try:
                pagination_page_size = int(query_dict["itemCountOnOnePage"])
                pagination_page_num = int(query_dict["pageIndex"])
                need_pagination = True
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild pagination request."
                }), status=400)

        all_files = CourseDocument.objects.filter(course_id=course_id)
        # newly updated file on top
        all_files = all_files.order_by('-file_update_timestamp')
        response = []
        if need_pagination:
            pagination_start = (pagination_page_num - 1) * pagination_page_size
            pagination_end = pagination_page_num * pagination_page_size
            select_files = all_files[pagination_start:pagination_end]
        else:
            select_files = all_files
        for item in select_files:
            response.append(CourseDocumentSerializer(item).data)
        return Response(response)

    def post(self, request, course_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # reject
            return Response(dict({
                    "msg": "Forbidden. You are not the teacher."
                }), status=403)
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)
        file_display_name = request_body["fileDisplayName"]
        random_hex_string = ('%030x' % random.randrange(16**30))
        file_token = f"{COURSE_DOCUMENT_PREFIX}/{course_id}/{random_hex_string}/{file_display_name}"
        new_course_file = CourseDocument(
            course_id=course_id,
            file_display_name=file_display_name,
            file_comment=request_body["fileComment"],
            file_create_timestamp=datetime.datetime.now(),
            file_update_timestamp=datetime.datetime.now(),

            file_uploader=request.user.user_id,
            file_token=file_token)
        new_course_file.file_token = file_token
        if not local_minio_client.bucket_exists(DEFAULT_BUCKET):
            local_minio_client.make_bucket(DEFAULT_BUCKET)
        post_url = local_minio_client.presigned_url("PUT",
                                                    DEFAULT_BUCKET,
                                                    file_token,
                                                    expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers = {
            "FILE_UPLOAD_URL": post_url
        }
        new_course_file.save()
        return Response(CourseDocumentSerializer(new_course_file).data,
                        headers=response_headers)


class CourseFileCountView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        content = {
            "course_id": course_id,
            "course_file_count": CourseDocument.objects.filter(course_id=course_id).count()
        }
        return Response(content)


class CourseFileMetaView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, file_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        
        file_queried: CourseDocument
        try:
            file_queried = CourseDocument.objects.get(course_id=course_id, file_course_document_id=file_id)
        except CourseDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested course document does not exist.",
                "courseId": course_id,
                "fileId": file_id
            }), status=404)

        return Response(CourseDocumentSerializer(file_queried).data)

    def put(self, request, course_id, file_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # reject
            return Response(dict({
                    "msg": "Forbidden. You are not the teacher."
                }), status=403)
        
        request_has_body = False
        request_body = None
        request_body_unicode = request.body.decode('utf-8')
        if len(request_body_unicode) != 0:
            try:
                request_body = json.loads(request_body_unicode)
                request_has_body = True
            except json.decoder.JSONDecodeError:
                return Response(dict({
                    "msg": "Invalid JSON string provided."
                }), status=400)
        else:
            return Response(dict({
                "msg": "Expect a JSON, but got empty contents instead."
            }), status=400)
        try:
            file_queried = CourseDocument.objects.get(course_id=course_id, file_course_document_id=file_id)
        except CourseDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested course document does not exist.",
                "courseId": course_id,
                "fileId": file_id
            }), status=404)
        file_queried.file_comment = request_body["fileComment"]
        file_queried.save()
        return Response(CourseDocumentSerializer(file_queried).data)

    def delete(self, request, course_id, file_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # reject
            return Response(dict({
                    "msg": "Forbidden. You are not the teacher."
                }), status=403)
        
        try:
            file_to_delete = CourseDocument.objects.get(course_id=course_id, file_course_document_id=file_id)
            item_token_to_delete = file_to_delete.file_token
            local_minio_client.remove_object(
                DEFAULT_BUCKET,
                item_token_to_delete
            )
            file_to_delete.delete()
        except CourseDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested course document does not exist.",
                "courseId": course_id,
                "fileId": file_id
            }), status=404)
        return Response(dict({
            "msg": "Deleted."
        }))


class CourseFileView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, file_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        file_queried: CourseDocument
        try:
            file_queried = CourseDocument.objects.get(course_id=course_id, file_course_document_id=file_id)
        except CourseDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested file does not exist.",
                "courseId": course_id,
                "fileId": file_id
            }), status=404)

        file_token = file_queried.file_token
        result_url = local_minio_client.presigned_url("GET",
                                                      DEFAULT_BUCKET,
                                                      file_token,
                                                      expires=DEFAULT_FILE_URL_TIMEOUT)

        return HttpResponseRedirect(redirect_to=result_url)

# Course file database ends
