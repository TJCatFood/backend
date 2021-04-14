from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

from .models import Announcement
from .serializers import AnnouncementSerializer

from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from course.utils import is_student_within_course, is_teacher_teach_course

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

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        query_dict = request.query_params
        need_pagination = False
        pagination_page_size = -1
        pagination_page_num = -1

        if query_dict:
            # find out whether the user requested for pagination
            try:
                pagination_page_size = int(query_dict["itemCountOnOnePage"])
                pagination_page_num = int(query_dict["pageIndex"])
                need_pagination = True
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild pagination request."
                }), status=400)

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
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # reject
            return Response(dict({
                    "msg": "Forbidden. You are not the teacher."
                }), status=403)
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)
        new_announcement = Announcement(
            course_id=course_id,
            announcement_title=request_body["announcementTitle"],
            announcement_contents=request_body["announcementContents"],
            announcement_is_pinned=request_body["announcementIsPinned"],
            announcement_publish_time=datetime.datetime.now(),
            announcement_last_update_time=datetime.datetime.now(),

            announcement_sender_id=request.user.user_id,
        )
        new_announcement.save()
        return Response(AnnouncementSerializer(new_announcement).data)


class AnnouncementCountView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        response = {
            "courseId": course_id,
            "announcementCount": Announcement.objects.filter(course_id=course_id).count()
        }
        return Response(response)


class AnnouncementIdView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, announcement_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        query_announcement = Announcement.objects.get(course_id=course_id, announcement_id=announcement_id)
        return Response(AnnouncementSerializer(query_announcement).data)

    def put(self, request, course_id, announcement_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            pass
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # check if this teacher teaches this course
            if not is_teacher_teach_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        elif user_character == 4:
            # student
            # reject
            return Response(dict({
                    "msg": "Forbidden. You are not the teacher."
                }), status=403)
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
