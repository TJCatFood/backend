from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Announcement

import json
import datetime


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


class AnnouncementController(APIView):

    def get(self, request, course_id, format=None):
        content = {
            "course_id": course_id,
        }
        announcement_list = Announcement.objects.filter(course_id=course_id)
        print(announcement_list)
        return Response(content)

    def post(self, request, course_id, format=None):
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)
        new_announcement = Announcement(
            course_id=course_id,
            announcement_title=request_body["announcementTitle"],
            announcement_contents=request_body["announcementContents"],
            announcement_is_pinned=request_body["announcementIsPinned"],
            announcement_publish_time=datetime.datetime.now(),
            announcement_last_update_time=datetime.datetime.now(),
            # waiting for user module
            announcement_sender_id=114514,
        )
        new_announcement.save()
