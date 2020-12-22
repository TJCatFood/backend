from django.apps import AppConfig

from minio import Minio
from minio import PostPolicy
from minio.error import ResponseError
from datetime import timedelta, datetime
from os import environ
import json

from catfood.settings import MINIO_STORAGE_MEDIA_BUCKET_NAME as DEFAULT_BUCKET
from catfood.settings import MINIO_STORAGE_USE_HTTPS

# AVATAR_BUCKET
AVATAR_PREFIX = "avatar"

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

# predefined anonymous read-only avatar policy

predefined_avatar_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{DEFAULT_BUCKET}/{AVATAR_PREFIX}/*",
        },
    ],
}


class AvatarConfig(AppConfig):
    name = 'avatar'
    verbose_name = "Catfood Avatar"

    def ready(self):
        local_minio_client.set_bucket_policy(DEFAULT_BUCKET, json.dumps(predefined_avatar_policy))
