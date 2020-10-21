from django.utils import timezone

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import connections
from django.db.utils import OperationalError

from django.core.cache import cache

class CatFoodStatusView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        time = timezone.localtime()
        db = 'down'
        redis = 'down'
        if self.db_connected():
            db = 'running'
        if self.redis_connected():
            redis = 'running'
        content = {"time": f"{time}",
                   "db": f"{db}",
                   "redis": f"{redis}"
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
