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


class AnnouncementView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, format=None):
        content = {
            "course_id": course_id,
        }

        request_body = None
        request_has_body = False
        need_pagination = False
        pagination_page_size = -1
        pagination_page_num = -1

        request_body_unicode = request.body.decode('utf-8')
        if len(request_body_unicode) != 0:
            try:
                request_body = json.loads(request_body_unicode)
                request_has_body = True
            except json.decoder.JSONDecodeError:
                return Response(dict({
                    "msg": "Invalid JSON string provided."
                }), status=400)

        if request_has_body:
            # find out whether the user requested for pagination
            try:
                pagination_page_size = request_body["itemCountOnOnePage"]
                pagination_page_num = request_body["pageIndex"]
                need_pagination = True
            except KeyError:
                pass

        response = []
        all_announcement = Announcement.objects.filter(course_id=course_id)
        all_announcement = all_announcement.order_by('announcement_id')

        if need_pagination:
            pagination_start = (pagination_page_num - 1) * pagination_page_size
            pagination_end = pagination_page_num * pagination_page_size
            selected_announcement = all_announcement[pagination_start:pagination_end]
        else:
            selected_announcement = all_announcement
        for item in selected_announcement:
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
            # FIXME: this user_id is for testing purpose only
            # waiting for user module
            announcement_sender_id=114514,
        )
        new_announcement.save()
        return Response(AnnouncementSerializer(new_announcement).data)


class AnnouncementCountView(APIView):
    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, format=None):
        response = {
            "courseId": course_id,
            "announcementCount": Announcement.objects.count()
        }
        return Response(response)


class AnnouncementIdView(APIView):
    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, course_id, announcement_id, format=None):
        query_announcement = Announcement.objects.get(course_id=course_id, announcement_id=announcement_id)
        return Response(AnnouncementSerializer(query_announcement).data)

    def put(self, request, course_id, announcement_id, format=None):
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
            query_announcement = Announcement.objects.get(course_id=course_id, announcement_id=announcement_id)
        except Announcement.DoesNotExist:
            return Response(dict({
                "msg": "Requested announcement does not exist.",
                "courseId": course_id,
                "announcement_id": announcement_id
            }), status=404)
        query_announcement.announcement_title = request_body["announcementTitle"]
        query_announcement.announcement_contents = request_body["announcementContents"]
        query_announcement.announcement_is_pinned = request_body["announcementIsPinned"]
        query_announcement.announcement_last_update_time = datetime.datetime.now()
        query_announcement.save()
        return Response(AnnouncementSerializer(query_announcement).data)

    def delete(self, request, course_id, announcement_id, format=None):
        try:
            announcement_to_delete = Announcement.objects.get(course_id=course_id, announcement_id=announcement_id)
            announcement_to_delete.delete()
        except Announcement.DoesNotExist:
            return Response(dict({
                "msg": "Requested announcement does not exist.",
                "courseId": course_id,
                "announcement_id": announcement_id
            }), status=404)
        return Response(dict({
            "msg": "Good."
        }))
