from rest_framework.response import Response
from rest_framework.views import APIView


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
