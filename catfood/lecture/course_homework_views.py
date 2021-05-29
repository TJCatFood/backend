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

from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher
from course.utils import is_student_within_course, is_teacher_teach_course

import json

from catfood.settings import MINIO_STORAGE_MEDIA_BUCKET_NAME as DEFAULT_BUCKET
from catfood.settings import MINIO_STORAGE_USE_HTTPS

from minio import Minio
from minio.error import ResponseError
from datetime import timedelta
from os import environ

import random


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

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/ 按照页码和每页数目获取某门课程下的作业列表
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
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

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
            homework_creator=request.user.user_id,
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

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/count 获取某门课共有多少作业
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
            "courseHomeworkCount": Homework.objects.filter(course_id=course_id).count()
        }
        return Response(response)


class HomeworkDataView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/{homeworkId} 获取某门课程下的某次作业详细信息（非提交文件）
    def get(self, request, course_id, homework_id, format=None):
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
        try:
            homework = Homework.objects.get(homework_id=homework_id)
            return Response(HomeworkSerializer(homework).data, status=status.HTTP_200_OK)
        except Homework.DoesNotExist:
            return Response(dict({
                "msg": "No such homework found."
            }), status=status.HTTP_404_NOT_FOUND)

    # /{courseId}/homework/{homeworkId} 更改作业信息（只有作业标题、作业描述、作业截止时间受影响，同时作业最后的更新时间会被更新）
    def put(self, request, course_id, homework_id, format=None):
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

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/{homeworkId}/file 学生提交作业（覆盖原有作业）
    def put(self, request, course_id, homework_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            # he/she should not handin homework!
            return Response(dict({
                "msg": "Forbidden. You should not handin homework."
            }), status=403)
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # these people should not handin homework!
            return Response(dict({
                "msg": "Forbidden. You should not handin homework."
            }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)

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
            file_to_delete = HomeworkFile.objects.get(file_uploader=request.user.user_id, homework_id=homework_id)
            # not this student
            if file_to_delete.file_uploader != user_id:
                return Response(dict({
                    "msg": "You can not change other student's submission :("
                }), status=403)
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
        file_token = f"{HOMEWORK_PREFIX}/{course_id}/{homework_id}/{request.user.user_id}/{random_hex_string}/{file_display_name}"
        new_course_file = HomeworkFile(
            homework_id=(Homework.objects.get(homework_id=homework_id)),
            file_comment=request_body["homeworkFileComment"],
            file_display_name=file_display_name,
            file_timestamp=datetime.now(),
            file_uploader=request.user.user_id,
            file_token=file_token)
        new_course_file.file_token = file_token
        if not local_minio_client.bucket_exists(DEFAULT_BUCKET):
            local_minio_client.make_bucket(DEFAULT_BUCKET)
        put_url = local_minio_client.presigned_url("PUT",
                                                   DEFAULT_BUCKET,
                                                   file_token,
                                                   expires=DEFAULT_FILE_URL_TIMEOUT)
        file_put_url_dict = {
            "FILE_PUT_URL": put_url
        }
        new_course_file.save()
        # This method is for Python 3.9+ only.
        final_dict_to_return = dict(HomeworkFileSerializer(new_course_file).data) | file_put_url_dict
        if replace_flag:
            return Response(final_dict_to_return, status=status.HTTP_200_OK)
        else:
            return Response(final_dict_to_return, status=status.HTTP_201_CREATED)

    # /{courseId}/homework/{homeworkId} 删除该学生这次作业的提交
    def delete(self, request, course_id, homework_id, format=None):
        user_character = request.user.character
        user_id = request.user.user_id
        # all within this class
        # TODO: change to match when comes to Python 3.10
        if user_character == 1:
            # charging teacher
            # he/she should not handin homework!
            return Response(dict({
                "msg": "Forbidden. You should not delete homework."
            }), status=403)
        elif user_character == 2 or user_character == 3:
            # teacher or teaching assistant
            # these people should not handin homework!
            return Response(dict({
                "msg": "Forbidden. You should not delete homework."
            }), status=403)
        elif user_character == 4:
            # student
            # check if student is within this course
            if not is_student_within_course(user_id, course_id):
                return Response(dict({
                    "msg": "Forbidden. You are not within course."
                }), status=403)
        try:
            file_to_delete = HomeworkFile.objects.get(homework_id=homework_id)
            # not this student
            if file_to_delete.file_uploader != user_id:
                return Response(dict({
                    "msg": "You can not change other student's submission :("
                }), status=403)
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

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/{homeworkId}/file/count 获取当前该作业下已提交作业列表中共有多少作业文件
    def get(self, request, course_id, homework_id, format=None):
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
        response = {
            "courseId": course_id,
            "courseHomeworkFileCount": HomeworkFile.objects.filter(homework_id=homework_id).count()
        }
        return Response(response)


class HomeworkFileView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/{homeworkId}/file/{homeworkFileId} 获取作业文件
    def get(self, request, course_id, homework_id, homework_file_id, format=None):
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
        file_queried: HomeworkFile
        try:
            file_queried = HomeworkFile.objects.get(homework_id=homework_id, file_homework_id=homework_file_id)
            # check student
            if user_character == 4:
                if file_queried.file_uploader != user_id:
                    return Response(dict({
                        "msg": "You can not read other student's submission :("
                    }), status=403)
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


class HomeworkFileUploaderView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/{homeworkId}/file/uploader/{fileUploader} 通过上传者 ID 获取作业文件信息
    # 该 API 暂未使用
    def get(self, request, course_id, homework_id, file_uploader, format=None):
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
            # check if student is query his own file id
            if not user_id == file_uploader:
                return Response(dict({
                    "msg": "You can not read other student's submission :("
                }), status=403)
        file_queried: HomeworkFile
        try:
            file_queried = HomeworkFile.objects.get(homework_id=homework_id, file_uploader=file_uploader)
        except HomeworkFile.DoesNotExist:
            return Response(dict({
                "msg": "Requested homework file does not exist.",
                "courseId": course_id,
                "studentId": file_uploader
            }), status=404)

        return Response(HomeworkFileSerializer(file_queried).data, status=status.HTTP_200_OK)


class HomeworkScoreView(APIView):

    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent |
                          IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    # /{courseId}/homework/{homeworkId}/score/{studentId} 根据学生 ID 获取作业分数
    def get(self, request, course_id, homework_id, student_id, format=None):
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
            # check if student is query his own file id
            if not user_id == student_id:
                return Response(dict({
                    "msg": "You can not read other student's submission :("
                }), status=403)

        score_queried: HomeworkScore
        try:
            score_queried = HomeworkScore.objects.get(homework_id=homework_id, student_id=student_id)
        except HomeworkScore.DoesNotExist:
            return Response(dict({
                "msg": "Requested homework score does not exist.",
                "courseId": course_id,
                "homeworkId": homework_id
            }), status=404)
        if score_queried.homework_is_grade_available_to_students == False and user_character == 4:
            return Response(dict({
                "msg": "Requested homework score is not available to students now.",
                "courseId": course_id,
                "homeworkId": homework_id
            }), status=403)

        return Response(HomeworkScoreSerializer(score_queried).data, status=status.HTTP_200_OK)

    # /{courseId}/homework/{homeworkId}/score/{studentId} 根据学生 ID 登记分数
    def put(self, request, course_id, homework_id, student_id, format=None):
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
        request_body = None
        if len(request_body_unicode) != 0:
            try:
                request_body = json.loads(request_body_unicode)
            except json.decoder.JSONDecodeError:
                return Response(dict({
                    "msg": "Invalid JSON string provided."
                }), status=status.HTTP_400_BAD_REQUEST)

        score_queried: HomeworkScore
        try:
            score_queried = HomeworkScore.objects.get(homework_id=homework_id, student_id=student_id)
            score_queried.homework_score = request_body["homeworkScore"]
            score_queried.homework_teachers_comments = request_body["homeworkTeachersComment"]
            score_queried.homework_is_grade_available_to_students = request_body["homeworkIsGradeAvailable"]
            score_queried.save()
        except HomeworkScore.DoesNotExist:
            score_queried = HomeworkScore(
                homework_id=(Homework.objects.get(homework_id=homework_id)),
                student_id=student_id,
                course_id=course_id,
                homework_score=request_body["homeworkScore"],
                homework_teachers_comments=request_body["homeworkTeachersComment"],
                homework_is_grade_available_to_students=request_body["homeworkIsGradeAvailable"],
            )
            score_queried.save()

        return Response(HomeworkScoreSerializer(score_queried).data, status=status.HTTP_200_OK)
