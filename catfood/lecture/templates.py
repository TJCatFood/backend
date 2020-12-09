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
        response = course_id
        content = {
            "course_id": f"{response}"
        }
        return Response(content)


class CourseIdHomeworkIdTemplate(APIView):

    def get(self, request, course_id, homework_id, format=None):
        content = {
            "course_id": course_id,
            "homework_id": homework_id
        }
        return Response(content)

# Too long!
# class CourseIdHomeworkIdHomeworkFileIdTemplate(APIView):


class CIHIHFI(APIView):
    def get(self, request, course_id, homework_id, homework_file_id, format=None):
        content = {
            "course_id": course_id,
            "homework_id": homework_id,
            "homework_file_id": homework_file_id
        }
        return Response(content)


class CourseIdChapterIdTemplate(APIView):

    def get(self, request, course_id, chapter_id, format=None):
        content = {
            "course_id": course_id,
            "chapter_id": chapter_id,
        }
        return Response(content)
