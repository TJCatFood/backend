from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny

from .models import Homework, HomeworkFile, HomeworkScore
from .serializers import HomeworkScoreSerializer, HomeworkFileSerializer, HomeworkSerializer

import json
