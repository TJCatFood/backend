from django.utils import timezone

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import connections
from django.db.utils import OperationalError

from django.core.cache import cache

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.storage import Storage
from django.core.files import File


class CatFoodStatusView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        time = timezone.localtime()
        db = 'down'
        redis = 'down'
        minio = 'down'
        if self.db_connected():
            db = 'running'
        if self.redis_connected():
            redis = 'running'
        if self.minio_connected():
            minio = 'running'
        content = {"time": f"{time}",
                   "db": f"{db}",
                   "redis": f"{redis}",
                   "minio": f"{minio}"
                   }
        return Response(content)

    def db_connected(self):
        conn = connections['default']
        try:
            conn.ensure_connection()
            return True
        except OperationalError:
            return False

    def redis_connected(self):
        time = timezone.localtime()
        try:
            cache.set('redis', time)
            return True
        except Exception:
            return False

    def minio_connected(self):
        try:
            testfile_content = b'minio here'
            path = default_storage.save('test/testfile', ContentFile(testfile_content))
            print(path)
            testfile_content_read = default_storage.open(path).read()
            default_storage.delete(path)
            return testfile_content == testfile_content_read:
        except Exception as e:
            return False
