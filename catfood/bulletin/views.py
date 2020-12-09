from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

from .models import Announcement
from .serializers import AnnouncementSerializer

import json
import datetime

class Announcement_:
    def __init__(self, announcement: Announcement):
        self.announcement_id = announcement.announcement_id
        self.course_id = announcement.course_id
        self.announcement_title = announcement.announcement_title
        self.announcement_contents = announcement.announcement_contents
        self.announcement_is_pinned = announcement.announcement_is_pinned
        self.announcement_publish_time = announcement.announcement_publish_time
        self.announcement_last_update_time = announcement.announcement_last_update_time
        self.announcement_sender_id = announcement.announcement_sender_id

class AliveView(APIView):

    def get(self, request, format=None):
        response = 'alive'
        content = {
            "response": f"{response}"
        }
        return Response(content)


class AnnouncementController(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, format=None):
        content = {
            "course_id": course_id,
        }
        response = []
        raw_announcement_list = Announcement.objects.filter(course_id=course_id)
        for item in raw_announcement_list:
            response.append(AnnouncementSerializer(item).data)
        return Response(response)

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
        return Response(AnnouncementSerializer(new_announcement).data)
