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

from .models import ExperimentDocument
from .serializers import ExperimentDocumentSerializer

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

# minio client to use
# TODO: when deployed and access through remote machine,
#       minio remote address should be changed to HTTP_HOST
#       with corresponding information.
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

# EXPERIMENT_DOCUMENT_BUCKET

EXPERIMENT_DOCUMENT_PREFIX = "experiment_document"

# Experiment file database starts


class ExperimentView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, experiment_id, format=None):
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

        all_files = ExperimentDocument.objects.filter(experiment_id=experiment_id)
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
            response.append(ExperimentDocumentSerializer(item).data)
        return Response(response)

    def post(self, request, experiment_id, format=None):
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)
        file_display_name = request_body["fileDisplayName"]
        random_hex_string = ('%030x' % random.randrange(16**30))
        file_token = f"{EXPERIMENT_DOCUMENT_PREFIX}/{experiment_id}/{random_hex_string}/{file_display_name}"
        new_experiment_file = ExperimentDocument(
            experiment_id=experiment_id,
            file_display_name=file_display_name,
            file_comment=request_body["fileComment"],
            file_create_timestamp=datetime.datetime.now(),
            file_update_timestamp=datetime.datetime.now(),
            # FIXME: this user_id is for testing purpose only
            # waiting for user module
            file_uploader=114514,
            file_token=file_token)
        new_experiment_file.file_token = file_token
        path = default_storage.save('catfood/alive', ContentFile(MINIO_FILE_PLACEHOLDER))
        default_storage.delete(path)
        post_url = local_minio_client.presigned_url("PUT",
                                                    DEFAULT_BUCKET,
                                                    file_token,
                                                    expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers = {
            "FILE_UPLOAD_URL": post_url
        }
        new_experiment_file.save()
        return Response(ExperimentDocumentSerializer(new_experiment_file).data,
                        headers=response_headers)


class ExperimentFileCountView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, experiment_id, format=None):
        content = {
            "experiment_id": experiment_id,
            "experiment_file_count": ExperimentDocument.objects.filter(experiment_id=experiment_id).count()
        }
        return Response(content)


class ExperimentFileMetaView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, experiment_id, file_id, format=None):
        file_queried: ExperimentDocument
        try:
            file_queried = ExperimentDocument.objects.get(experiment_id=experiment_id, file_experiment_document_id=file_id)
        except ExperimentDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested experiment document does not exist.",
                "experimentId": experiment_id,
                "fileId": file_id
            }), status=404)

        return Response(ExperimentDocumentSerializer(file_queried).data)

    def put(self, request, experiment_id, file_id, format=None):
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
            file_queried = ExperimentDocument.objects.get(experiment_id=experiment_id, file_experiment_document_id=file_id)
        except ExperimentDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested experiment document does not exist.",
                "experimentId": experiment_id,
                "fileId": file_id
            }), status=404)
        file_queried.file_comment = request_body["fileComment"]
        file_queried.save()
        return Response(ExperimentDocumentSerializer(file_queried).data)

    def delete(self, request, experiment_id, file_id, format=None):
        try:
            file_to_delete = ExperimentDocument.objects.get(experiment_id=experiment_id, file_experiment_document_id=file_id)
            item_token_to_delete = file_to_delete.file_token
            local_minio_client.remove_object(
                DEFAULT_BUCKET,
                item_token_to_delete
            )
            file_to_delete.delete()
        except ExperimentDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested experiment document does not exist.",
                "experimentId": experiment_id,
                "fileId": file_id
            }), status=404)
        return Response(dict({
            "msg": "Deleted."
        }))


class ExperimentFileView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, experiment_id, file_id, format=None):
        file_queried: ExperimentDocument
        try:
            file_queried = ExperimentDocument.objects.get(experiment_id=experiment_id, file_experiment_document_id=file_id)
        except ExperimentDocument.DoesNotExist:
            return Response(dict({
                "msg": "Requested file does not exist.",
                "experimentId": experiment_id,
                "fileId": file_id
            }), status=404)

        file_token = file_queried.file_token
        result_url = local_minio_client.presigned_url("GET",
                                                      DEFAULT_BUCKET,
                                                      file_token,
                                                      expires=DEFAULT_FILE_URL_TIMEOUT)

        return HttpResponseRedirect(redirect_to=result_url)

# Experiment file database ends
