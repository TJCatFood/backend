from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view


class AliveView(APIView):

    def get(self, request, format=None):
        response = 'alive'
        content = {
            "response": f"{response}"
        }
        return Response(content)


class CourseIdTemplate(APIView):

    def get(self, request, course_id, format=None):
        content = {
            "course_id": course_id,
        }
        return Response(content)

class CourseIdAnnouncementIdTemplate(APIView):

    def get(self, request, course_id, announcement_id, format=None):
        content = {
            "course_id": course_id,
            "announcement_id": announcement_id,
        }
        return Response(content)