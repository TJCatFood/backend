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


from typing import Union

import json
import datetime
from enum import IntEnum

from minio import Minio
from minio import PostPolicy
from minio.error import ResponseError
from datetime import timedelta, datetime
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

# AVATAR_BUCKET
AVATAR_PREFIX = "avatar"

# MAX AVATAR SIZE (MB)
MAX_AVATAR_SIZE = 4 * 1024 * 1024


def generate_avatar_token(user_id: int) -> str:
    return f"{AVATAR_PREFIX}/{user_id}/avatar"


class AvatarView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, user_id, format=None):
        file_token = generate_avatar_token(user_id)

        # old presigned method
        # result_url = local_minio_client.presigned_url("GET",
        #                                               DEFAULT_BUCKET,
        #                                               file_token,
        #                                               expires=DEFAULT_FILE_URL_TIMEOUT)

        # now the folder is public
        result_url_scheme = "https" if MINIO_STORAGE_USE_HTTPS else "http"
        result_url = f"{result_url_scheme}://{environ['MINIO_ADDRESS']}/{DEFAULT_BUCKET}/{file_token}"
        return HttpResponseRedirect(redirect_to=result_url)

    def put(self, request, user_id, format=None):
        post_policy = PostPolicy()
        # set bucket name location for uploads.
        post_policy.set_bucket_name(DEFAULT_BUCKET)
        # set key prefix for all incoming uploads.
        file_token = generate_avatar_token(user_id)
        post_policy.set_key_startswith(file_token)
        # set content length for incoming uploads.
        post_policy.set_content_length_range(0, MAX_AVATAR_SIZE)

        # set expiry
        expires_date = datetime.utcnow() + DEFAULT_FILE_URL_TIMEOUT
        post_policy.set_expires(expires_date)

        post_policy

        url, signed_form_data = local_minio_client.presigned_post_policy(post_policy)
        response = {
            "url": url,
            "request_form": signed_form_data
        }
        return Response(response)
