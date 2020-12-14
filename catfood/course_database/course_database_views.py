from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.db import models

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view

from rest_framework.permissions import AllowAny

from .models import CourseDocument
from .serializers import CourseDocumentSerializer

from typing import Union

import json
import datetime
from enum import IntEnum

from minio import Minio
from minio.error import ResponseError
from datetime import timedelta
from os import environ

from catfood.settings import MINIO_STORAGE_MEDIA_BUCKET_NAME as DEFAULT_BUCKET

import random

# minio client to use
# TODO: when deployed and access through remote machine,
#       minio remote address should be changed to HTTP_HOST
#       with corresponding information.
local_minio_client = Minio(
    environ['MINIO_ADDRESS'],
    access_key=environ['MINIO_ACCESS_KEY'],
    secret_key=environ['MINIO_SECRET_KEY'],
    secure=False,
)

# default file URL timeout = 15 min
DEFAULT_FILE_URL_TIMEOUT = timedelta(minutes=15)

# placeholder for new file
MINIO_FILE_PLACEHOLDER = b"THIS IS A PLACEHOLDER FOR NEW FILE"

# COURSE_DOCUMENT_BUCKET

COURSE_DOCUMENT_PREFIX = "course_document"

# Course file database starts


class CourseView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, format=None):
        request_body = None
        request_has_body = False
        need_pagination = False
        pagination_page_size = -1
        pagination_page_num = -1

        request_body_unicode = request.body.decode('utf-8')
        if len(request_body_unicode) != 0:
            try:
                request_body = json.loads(request_body_unicode)
                request_has_body = True
            except json.decoder.JSONDecodeError:
                return Response(dict({
                    "msg": "Invalid JSON string provided."
                }), status=400)

        if request_has_body:
            # find out whether the user requested for pagination
            try:
                pagination_page_size = request_body["itemCountOnOnePage"]
                pagination_page_num = request_body["pageIndex"]
                need_pagination = True
            except KeyError:
                pass

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
            # FIXME: this user_id is for testing purpose only
            # waiting for user module
            file_uploader=114514,
            file_token=file_token)
        new_course_file.file_token = file_token
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

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, format=None):
        content = {
            "course_id": course_id,
            "course_file_count": CourseDocument.objects.filter(course_id=course_id).count()
        }
        return Response(content)


class CourseFileMetaView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, file_id, format=None):
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
        file_queried.announcement_title = request_body["fileComments"]
        file_queried.save()
        return Response(CourseDocumentSerializer(file_queried).data)

    def delete(self, request, course_id, file_id, format=None):
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
                "msg": "Requested announcement does not exist.",
                "courseId": course_id,
                "fileId": file_id
            }), status=404)
        return Response(dict({
            "msg": "Deleted."
        }))


class CourseFileView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, file_id, format=None):
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
