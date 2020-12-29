from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.http.response import HttpResponseRedirect

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from django.utils import timezone as datetime

from .models import Homework, HomeworkFile, HomeworkScore
from .serializers import HomeworkFileSerializer, HomeworkSerializer, HomeworkScoreSerializer

import json

from catfood.settings import MINIO_STORAGE_MEDIA_BUCKET_NAME as DEFAULT_BUCKET
from catfood.settings import MINIO_STORAGE_USE_HTTPS

from minio import Minio
from minio.error import ResponseError
from datetime import timedelta
from os import environ

import random

# minio client to use
# TODO: when deployed and access through remote machine,
#       minio remote address should be changed to HTTP_HOST
#       with corresponding information.
local_minio_client = Minio(
    environ['MINIO_ADDRESS'],
    access_key=environ['MINIO_ACCESS_KEY'],
    secret_key=environ['MINIO_SECRET_KEY'],
    secure=MINIO_STORAGE_USE_HTTPS,
)

# default file URL timeout = 15 min
DEFAULT_FILE_URL_TIMEOUT = timedelta(minutes=15)

# placeholder for new file
MINIO_FILE_PLACEHOLDER = b"THIS IS A PLACEHOLDER FOR NEW FILE"

# HOMEWORK_PREFIX_BUCKET

HOMEWORK_PREFIX = "homework"

# FIXME:A tmp user for test use

TEST_USER = 114514


class HomeworkView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    # /{courseId}/homework/ 按照页码和每页数目获取某门课程下的作业列表
    def get(self, request, course_id, format=None):
        query_dict = request.query_params

        need_pagination = False
        pagination_page_size = -1
        pagination_page_num = -1

        if len(query_dict) != 0:
            try:
                pagination_page_num = int(query_dict['pageIndex'])
                pagination_page_size = int(query_dict['itemCountOnOnePage'])
                need_pagination = True
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild pagination request."
                }), status=status.HTTP_400_BAD_REQUEST)

        response = []
        all_homework = Homework.objects.filter(course_id=course_id)\
            .order_by('homework_id')

        if need_pagination:
            pagination_start = (pagination_page_num - 1) * pagination_page_size
            pagination_end = pagination_page_num * pagination_page_size
            selected_homework = all_homework[pagination_start:pagination_end]
        else:
            selected_homework = all_homework
        for item in selected_homework:
            response.append(HomeworkSerializer(item).data)

        return Response(response, status=status.HTTP_200_OK)

    # /{courseId}/homework/ 创建一次新作业
    def post(self, request, course_id, format=None):

        request_body_unicode = request.body.decode('utf-8')
        if len(request_body_unicode) != 0:
            try:
                request_body = json.loads(request_body_unicode)
            except json.decoder.JSONDecodeError:
                return Response(dict({
                    "msg": "Invalid JSON string provided."
                }), status=status.HTTP_400_BAD_REQUEST)

        request_body = json.loads(request_body_unicode)
        new_homework = Homework(
            course_id=course_id,
            homework_creator=TEST_USER,
            homework_title=request_body["homeworkTitle"],
            homework_description=request_body["homeworkDescription"],
            homework_start_timestamp=request_body["homeworkStartTime"],
            homework_end_timestamp=request_body["homeworkEndTime"],
            homework_create_timestamp=datetime.now(),
            homework_update_timestamp=datetime.now(),
        )

        if new_homework.homework_start_timestamp > new_homework.homework_end_timestamp:
            return Response(dict({
                "msg": "End before start."
            }), status=status.HTTP_400_BAD_REQUEST)

        try:
            new_homework.save()
        except ValidationError as e:
            return Response(dict({
                "msg": f"Invalid parameter. Detail: {e.message}"
            }), status=status.HTTP_400_BAD_REQUEST)

        return Response(HomeworkSerializer(new_homework).data, status=status.HTTP_201_CREATED)


class HomeworkCountView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    # /{courseId}/homework/count 获取某门课共有多少作业
    def get(self, request, course_id, format=None):
        response = {
            "courseId": course_id,
            "courseHomeworkCount": Homework.objects.filter(course_id=course_id).count()
        }
        return Response(response)


class HomeworkDataView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    # /{courseId}/homework/{homeworkId} 获取某门课程下的某次作业详细信息（非提交文件）
    def get(self, request, course_id, homework_id, format=None):

        try:
            homework = Homework.objects.get(homework_id=homework_id)
            return Response(HomeworkSerializer(homework).data, status=status.HTTP_200_OK)
        except Homework.DoesNotExist:
            return Response(dict({
                "msg": "No such homework found."
            }), status=status.HTTP_404_NOT_FOUND)

    # /{courseId}/homework/{homeworkId} 更改作业信息（只有作业标题、作业描述、作业截止时间受影响，同时作业最后的更新时间会被更新）
    def put(self, request, course_id, homework_id, format=None):

        request_body_unicode = request.body.decode('utf-8')
        if len(request_body_unicode) != 0:
            try:
                request_body = json.loads(request_body_unicode)
            except json.decoder.JSONDecodeError:
                return Response(dict({
                    "msg": "Invalid JSON string provided."
                }), status=status.HTTP_400_BAD_REQUEST)

        try:
            homework = Homework.objects.get(course_id=course_id, homework_id=homework_id)
        except Homework.DoesNotExist:
            return Response(dict({
                "msg": "No such homework found."
            }), status=status.HTTP_404_NOT_FOUND)

        request_body = json.loads(request_body_unicode)
        homework.homework_title = request_body["homeworkTitle"]
        homework.homework_description = request_body["homeworkDescription"]
        homework.homework_start_timestamp = request_body["homeworkStartTime"]
        homework.homework_end_timestamp = request_body["homeworkEndTime"]
        homework.homework_update_timestamp = datetime.now()

        if homework.homework_start_timestamp > homework.homework_end_timestamp:
            return Response(dict({
                "msg": "End before start."
            }), status=status.HTTP_400_BAD_REQUEST)

        homework.save()

        return Response(HomeworkSerializer(homework).data, status=status.HTTP_200_OK)

    # /{courseId}/homework/{homeworkId} 删除这个作业
    def delete(self, request, course_id, homework_id, format=None):

        try:
            homework = Homework.objects.get(course_id=course_id, homework_id=homework_id)
            homework.delete()
            # FIXME: 外码约束，删除文件和学生提交记录和分数
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Homework.DoesNotExist:
            return Response(dict({
                "msg": "No such homework found."
            }), status=status.HTTP_404_NOT_FOUND)


class HomeworkDataFileView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    # /{courseId}/homework/{homeworkId}/file 学生提交作业（覆盖原有作业）
    def put(self, request, course_id, homework_id, format=None):

        replace_flag = False

        try:
            homework = Homework.objects.get(homework_id=homework_id)
        except Homework.DoesNotExist:
            return Response(dict({
                "msg": "No such homework found."
            }), status=status.HTTP_404_NOT_FOUND)

        if homework.homework_end_timestamp < datetime.now():
            return Response(dict({
                "msg": "You can not submit after the deadline."
            }), status=status.HTTP_400_BAD_REQUEST)

        try:
            # FIXME: get student_id from token.
            file_to_delete = HomeworkFile.objects.get(file_uploader=TEST_USER, homework_id=homework_id)
            item_token_to_delete = file_to_delete.file_token
            local_minio_client.remove_object(
                DEFAULT_BUCKET,
                item_token_to_delete
            )
            file_to_delete.delete()
        except HomeworkFile.DoesNotExist:
            replace_flag = True
            pass

        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)
        file_display_name = request_body["homeworkFileDisplayName"]
        random_hex_string = ('%030x' % random.randrange(16**30))
        file_token = f"{HOMEWORK_PREFIX}/{course_id}/{homework_id}/{TEST_USER}/{random_hex_string}/{file_display_name}"
        new_course_file = HomeworkFile(
            homework_id=(Homework.objects.get(homework_id=homework_id)),
            file_comment=request_body["homeworkFileComment"],
            file_display_name=file_display_name,
            file_timestamp=datetime.now(),
            # FIXME: this user_id is for testing purpose only
            # waiting for user module
            file_uploader=TEST_USER,
            file_token=file_token)
        new_course_file.file_token = file_token
        path = default_storage.save('catfood/alive', ContentFile(MINIO_FILE_PLACEHOLDER))
        default_storage.delete(path)
        post_url = local_minio_client.presigned_url("PUT",
                                                    DEFAULT_BUCKET,
                                                    file_token,
                                                    expires=DEFAULT_FILE_URL_TIMEOUT)
        response_headers = {
            "FILE_UPLOAD_URL": post_url
        }
        new_course_file.save()

        if replace_flag:
            return Response(HomeworkFileSerializer(new_course_file).data,
                            headers=response_headers, status=status.HTTP_200_OK)
        else:
            return Response(HomeworkFileSerializer(new_course_file).data,
                            headers=response_headers, status=status.HTTP_201_CREATED)

    # /{courseId}/homework/{homeworkId} 删除该学生这次作业的提交
    def delete(self, request, course_id, homework_id, format=None):

        try:
            # FIXME: get student_id from token.
            file_to_delete = HomeworkFile.objects.get(file_uploader=TEST_USER, homework_id=homework_id)
            item_token_to_delete = file_to_delete.file_token
            local_minio_client.remove_object(
                DEFAULT_BUCKET,
                item_token_to_delete
            )
            file_to_delete.delete()
        except HomeworkFile.DoesNotExist:
            return Response(dict({
                "msg": "Requested homework file does not exist.",
                "courseId": course_id,
                "fileId": homework_id
            }), status=status.HTTP_404_NOT_FOUND)
        return Response(dict({
            "msg": "Deleted."
        }))

    # /{courseId}/homework/{homeworkId}/file 按照页码和每页数目获取某门课的作业文件列表
    def get(self, request, course_id, homework_id, format=None):
        query_dict = request.query_params

        need_pagination = False
        pagination_page_size = -1
        pagination_page_num = -1

        if len(query_dict) != 0:
            try:
                pagination_page_num = int(query_dict['pageIndex'])
                pagination_page_size = int(query_dict['itemCountOnOnePage'])
                need_pagination = True
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild pagination request."
                }), status=status.HTTP_400_BAD_REQUEST)

        response = []
        all_homeworkFiles = HomeworkFile.objects.filter(homework_id=homework_id)\
            .order_by('homework_id')

        if need_pagination:
            pagination_start = (pagination_page_num - 1) * pagination_page_size
            pagination_end = pagination_page_num * pagination_page_size
            selected_homeworkFiles = all_homeworkFiles[pagination_start:pagination_end]
        else:
            selected_homeworkFiles = all_homeworkFiles
        for item in selected_homeworkFiles:
            response.append(HomeworkFileSerializer(item).data)

        return Response(response, status=status.HTTP_200_OK)


class HomeworkDataFileCountView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    # /{courseId}/homework/{homeworkId}/file/count 获取当前该作业下已提交作业列表中共有多少作业文件
    def get(self, request, course_id, homework_id, format=None):
        response = {
            "courseId": course_id,
            "courseHomeworkFileCount": HomeworkFile.objects.filter(homework_id=homework_id).count()
        }
        return Response(response)


class HomeworkFileView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    # /{courseId}/homework/{homeworkId}/file/{homeworkFileId} 获取作业文件
    def get(self, request, course_id, homework_id, homework_file_id, format=None):
        file_queried: HomeworkFile
        try:
            file_queried = HomeworkFile.objects.get(homework_id=homework_id, file_homework_id=homework_file_id)
        except HomeworkFile.DoesNotExist:
            return Response(dict({
                "msg": "Requested homework file does not exist.",
                "courseId": course_id,
                "homeworkFileId": homework_file_id
            }), status=404)

        file_token = file_queried.file_token
        result_url = local_minio_client.presigned_url("GET",
                                                      DEFAULT_BUCKET,
                                                      file_token,
                                                      expires=DEFAULT_FILE_URL_TIMEOUT)

        return HttpResponseRedirect(redirect_to=result_url)


class HomeworkFileScoreView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    # /{courseId}/homework/{homeworkId}/file/{homeworkFileId}/score 获取作业分数
    def get(self, request, course_id, homework_id, homework_file_id, format=None):

        # FIXME: get student id from token.
        try:
            file_queried = HomeworkScore.objects.get(homework_id=homework_id, student_id=TEST_USER)
        except HomeworkScore.DoesNotExist:
            return Response(dict({
                "msg": "Requested homework file does not exist.",
                "courseId": course_id,
                "homeworkId": homework_id
            }), status=404)

        return Response(HomeworkScoreSerializer(file_queried).data, status=status.HTTP_200_OK)

    # /{courseId}/homework/{homeworkId}/file/{homeworkFileId}/score 根据文件 ID 登记分数
    def put(self, request, course_id, homework_id, homework_file_id, format=None):

        request_body_unicode = request.body.decode('utf-8')
        request_body = None
        if len(request_body_unicode) != 0:
            try:
                request_body = json.loads(request_body_unicode)
            except json.decoder.JSONDecodeError:
                return Response(dict({
                    "msg": "Invalid JSON string provided."
                }), status=status.HTTP_400_BAD_REQUEST)

        try:
            file_queried = HomeworkFile.objects.get(file_homework_id=homework_file_id)
        except HomeworkFile.DoesNotExist as e:
            print(e.with_traceback)
            return Response(dict({
                "msg": "Requested homework file does not exist.",
                "courseId": course_id,
                "homeworkFileId": homework_file_id
            }), status=404)

        try:
            file_score_queried = HomeworkScore.objects.get(homework_id=homework_id, student_id=file_queried.file_uploader)
            file_score_queried.homework_score = request_body["homeworkScore"]
            file_score_queried.homework_teachers_comments = request_body["homeworkTeachersComment"]
            file_score_queried.homework_is_grade_available_to_students = request_body["homeworkIsGradeAvailable"]
            file_score_queried.save()
        except HomeworkScore.DoesNotExist:
            file_score_queried = HomeworkScore(
                homework_id=(Homework.objects.get(homework_id=homework_id)),
                student_id=file_queried.file_uploader,
                course_id=course_id,
                homework_score=request_body["homeworkScore"],
                homework_teachers_comments=request_body["homeworkTeachersComment"],
                homework_is_grade_available_to_students=request_body["homeworkIsGradeAvailable"],
            )
            file_score_queried.save()

        return Response(HomeworkScoreSerializer(file_score_queried).data, status=status.HTTP_200_OK)
