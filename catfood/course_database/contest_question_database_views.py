from django.db.models.query import QuerySet
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.db import models

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view

from rest_framework.permissions import AllowAny

from .models import MultipleChoiceQuestion, SingleChoiceQuestion

from typing import Union

import json
import random
from enum import IntEnum


class QuestionType(IntEnum):
    SINGLE_CHOICE = 0
    MULTIPLE_CHOICE = 1
    UNKNOWN = -2


class Question:
    def __init__(self, item: Union[SingleChoiceQuestion, MultipleChoiceQuestion]):
        self.question_id = item.question_id
        self.question_chapter = item.question_chapter
        self.question_content = item.question_content
        self.question_choice_a_content = item.question_choice_a_content
        self.question_choice_b_content = item.question_choice_b_content
        self.question_choice_c_content = item.question_choice_c_content
        self.question_choice_d_content = item.question_choice_d_content
        self.question_answer = item.question_answer
        if type(item) == SingleChoiceQuestion:
            self.question_type = QuestionType.SINGLE_CHOICE
        elif type(item) == MultipleChoiceQuestion:
            self.question_type = QuestionType.MULTIPLE_CHOICE
        else:
            self.question_type = QuestionType.UNKNOWN

# Contest question database starts


class QuestionView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        query_dict = request.query_params

        need_filter = False
        requested_question_type = -1
        need_pagination = False
        pagination_page_size = -1
        pagination_page_num = -1
        need_to_select_from_chapter = False
        chapter_start = -1
        chapter_end = -1

        if query_dict:
            # find out whether the user requested for specific type of question
            try:
                requested_question_type = query_dict["questionType"]
                need_filter = True
            except KeyError:
                pass

            # find out whether the user requested for pagination
            try:
                pagination_page_size = int(query_dict["pageSize"])
                pagination_page_num = int(query_dict["pageNum"])
                need_pagination = True
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild pagination request."
                }), status=400)

            # find out whether the user requested for
            # question falls in chapter ranging from start and end
            try:
                chapter_start = int(query_dict["chapterStart"])
                chapter_end = int(query_dict["chapterEnd"])
                if chapter_start > chapter_end:
                    return Response(dict({
                        "msg": "Invaild chapter selection request: "
                        "start index is larger than end index"
                    }), status=400)
                need_to_select_from_chapter = True
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild chapter selection request."
                }), status=400)

        all_questions = []
        if need_filter:
            try:
                if int(requested_question_type) == QuestionType.SINGLE_CHOICE:
                    all_single_choice_questions = SingleChoiceQuestion.objects.all()
                    for item in all_single_choice_questions:
                        all_questions.append(Question(item))
                elif int(requested_question_type) == QuestionType.MULTIPLE_CHOICE:
                    all_multiple_choice_questions = MultipleChoiceQuestion.objects.all()
                    for item in all_multiple_choice_questions:
                        all_questions.append(Question(item))
                else:
                    return Response(dict({
                        "msg": "question_type wants to fuck you"
                    }), status=400)
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "question_type is not an int"
                }), status=400)
        else:
            all_single_choice_questions = SingleChoiceQuestion.objects.all()
            for item in all_single_choice_questions:
                all_questions.append(Question(item))
            all_multiple_choice_questions = MultipleChoiceQuestion.objects.all()
            for item in all_multiple_choice_questions:
                all_questions.append(Question(item))

        if need_to_select_from_chapter:
            all_questions_original = all_questions
            all_questions = []
            item: Question
            for item in all_questions_original:
                if chapter_start <= item.question_chapter <= chapter_end:
                    all_questions.append(item)

        response = {
            "questions": [],
            "pagination": None
        }

        # calcs the pagination
        if need_pagination:
            single_choice_questions_count = SingleChoiceQuestion.objects.count()
            multiple_choice_questions_count = MultipleChoiceQuestion.objects.count()
            question_count = single_choice_questions_count + multiple_choice_questions_count
            response["pagination"] = dict(
                {
                    "pageNum": pagination_page_num,
                    "pageSize": pagination_page_size,
                    "total": question_count
                }
            )
            pagination_start = (pagination_page_num - 1) * pagination_page_size
            pagination_end = pagination_page_num * pagination_page_size
            selected_questions = all_questions[pagination_start:pagination_end]
        else:
            selected_questions = all_questions
        for item in selected_questions:
            response["questions"].append({
                "questionId": item.question_id,
                "questionType": item.question_type,
                "questionChapter": item.question_chapter,
                "questionContent": item.question_content,
                "questionChoiceAContent": item.question_choice_a_content,
                "questionChoiceBContent": item.question_choice_b_content,
                "questionChoiceCContent": item.question_choice_c_content,
                "questionChoiceDContent": item.question_choice_d_content,
                "questionAnswer": item.question_answer,
            })
        return Response(response)

    def post(self, request, format=None):
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)["question"]
        try:
            question_type = request_body["questionType"]
            if question_type == QuestionType.SINGLE_CHOICE:
                new_question = SingleChoiceQuestion(
                    question_chapter=request_body["questionChapter"],
                    question_content=request_body["questionContent"],
                    question_choice_a_content=request_body["questionChoiceAContent"],
                    question_choice_b_content=request_body["questionChoiceBContent"],
                    question_choice_c_content=request_body["questionChoiceCContent"],
                    question_choice_d_content=request_body["questionChoiceDContent"],
                    question_answer=request_body["questionAnswer"],
                )
            elif question_type == QuestionType.MULTIPLE_CHOICE:
                new_question = MultipleChoiceQuestion(
                    question_chapter=request_body["questionChapter"],
                    question_content=request_body["questionContent"],
                    question_choice_a_content=request_body["questionChoiceAContent"],
                    question_choice_b_content=request_body["questionChoiceBContent"],
                    question_choice_c_content=request_body["questionChoiceCContent"],
                    question_choice_d_content=request_body["questionChoiceDContent"],
                    question_answer=request_body["questionAnswer"],
                )
            else:
                return Response(dict({
                    "msg": "question_type wants to fuck you"
                }), status=400)
            new_question.save()
            return Response(request_body)
        except Exception:
            return Response(dict({
                "msg": "Generic exception."
            }), status=400)


class QuestionCountView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        single_choice_questions_count = SingleChoiceQuestion.objects.count()
        multiple_choice_questions_count = MultipleChoiceQuestion.objects.count()
        question_count = single_choice_questions_count + multiple_choice_questions_count
        content = {
            "question_count": question_count
        }
        return Response(content)


class QuestionIdView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, question_type, question_id, format=None):
        item = None
        if question_type == QuestionType.SINGLE_CHOICE:
            item = SingleChoiceQuestion.objects.get(question_id=question_id)

        elif question_type == QuestionType.MULTIPLE_CHOICE:
            item = MultipleChoiceQuestion.objects.get(question_id=question_id)
        else:
            return Response(dict({
                "msg": "question_type wants to fuck you"
            }), status=400)
        response = {
            "questionId": item.question_id,
            "questionType": question_type,
            "questionChapter": item.question_chapter,
            "questionContent": item.question_content,
            "questionChoiceAContent": item.question_choice_a_content,
            "questionChoiceBContent": item.question_choice_b_content,
            "questionChoiceCContent": item.question_choice_c_content,
            "questionChoiceDContent": item.question_choice_d_content,
            "questionAnswer": item.question_answer,
        }
        return Response(response)

    def put(self, request, question_type, question_id, format=None):
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)["question"]
        try:
            if question_type == QuestionType.SINGLE_CHOICE:
                old_question = SingleChoiceQuestion.objects.get(question_id=question_id)
                old_question.question_chapter = request_body["questionChapter"]
                old_question.question_content = request_body["questionContent"]
                old_question.question_choice_a_content = request_body["questionChoiceAContent"]
                old_question.question_choice_b_content = request_body["questionChoiceBContent"]
                old_question.question_choice_c_content = request_body["questionChoiceCContent"]
                old_question.question_choice_d_content = request_body["questionChoiceDContent"]
                old_question.question_answer = request_body["questionAnswer"]

            elif question_type == QuestionType.MULTIPLE_CHOICE:
                old_question = MultipleChoiceQuestion.objects.get(question_id=question_id)
                old_question.question_chapter = request_body["questionChapter"]
                old_question.question_content = request_body["questionContent"]
                old_question.question_choice_a_content = request_body["questionChoiceAContent"]
                old_question.question_choice_b_content = request_body["questionChoiceBContent"]
                old_question.question_choice_c_content = request_body["questionChoiceCContent"]
                old_question.question_choice_d_content = request_body["questionChoiceDContent"]
                old_question.question_answer = request_body["questionAnswer"]
            else:
                return Response(dict({
                    "msg": "question_type wants to fuck you"
                }), status=400)
            old_question.save()
            return Response(request_body)
        except Exception:
            return Response(dict({
                "msg": "Generic exception."
            }), status=400)

    def delete(self, request, question_type, question_id, format=None):

        try:
            if question_type == QuestionType.SINGLE_CHOICE:
                question_to_delete = SingleChoiceQuestion.objects.get(question_id=question_id)
            elif question_type == QuestionType.MULTIPLE_CHOICE:
                question_to_delete = MultipleChoiceQuestion.objects.get(question_id=question_id)
            else:
                return Response(dict({
                    "msg": "question_type wants to fuck you"
                }), status=400)
        except SingleChoiceQuestion.DoesNotExist:
            return Response(dict({
                "msg": "Requested question does not exist.",
                "question_type": QuestionType.SINGLE_CHOICE
            }), status=404)
        except MultipleChoiceQuestion.DoesNotExist:
            return Response(dict({
                "msg": "Requested question does not exist.",
                "question_type": QuestionType.MULTIPLE_CHOICE
            }), status=404)
        question_to_delete.delete()
        return Response(dict({
            "msg": "Good."
        }))


class RandomQuestionView(APIView):

    # FIXME: this permission is for testing purpose only
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        query_dict = request.query_params
        need_to_select_from_chapter = False
        chapter_start = -1
        chapter_end = -1

        single_choice_question_num = -1
        multiple_choice_question_num = -1

        if query_dict:
            # find out whether the user requested for
            # question falls in chapter ranging from start and end
            try:
                chapter_start = int(query_dict["chapterStart"])
                chapter_end = int(query_dict["chapterEnd"])
                if chapter_start > chapter_end:
                    return Response(dict({
                        "msg": "Invaild chapter selection request: "
                        "start index is larger than end index"
                    }), status=400)
                need_to_select_from_chapter = True
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild chapter selection request."
                }), status=400)
            try:
                single_choice_question_num = int(query_dict["singleChoiceQuestionNum"])
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    "msg": "Invaild singleChoiceQuestionNum request."
                }), status=400)
            try:
                multiple_choice_question_num = int(query_dict["multipleChoiceQuestionNum"])
            except KeyError:
                pass
            except ValueError:
                # not an int
                return Response(dict({
                    << << << < HEAD
                    "msg": "Invaild multipleChoiceQuestionNum request."
                    == == == =
                    "msg": "Invaild mutipleChoiceQuestionNum request."
                    >> >>>> > 3c8b0236903369a3ca89a5ee7ece0c7fadb8a9ec
                }), status=400)
        if single_choice_question_num == multiple_choice_question_num == -1:
            return Response(dict({
                "msg": "You should provide a limit for at least one kind of question."
            }), status=400)

        response = {
            "questions": [],
            "single_choice_question_stats": False,
            "multiple_choice_question_stats": False,
        }

        all_single_choice_questions_list = []
        all_multiple_choice_questions_list = []
        selected_random_single_choice_questions = []
        selected_random_multiple_choice_questions = []

        if single_choice_question_num != -1:
            all_single_choice_questions_queryset = SingleChoiceQuestion.objects.all()
            for item in all_single_choice_questions_queryset:
                all_single_choice_questions_list.append(Question(item))
            selected_single_choice_questions_list = all_single_choice_questions_list
            if need_to_select_from_chapter:
                selected_single_choice_questions_list = []
                item: Question
                for item in all_single_choice_questions_list:
                    if chapter_start <= item.question_chapter <= chapter_end:
                        selected_single_choice_questions_list.append(item)
            if len(selected_single_choice_questions_list) >= single_choice_question_num:
                response["single_choice_question_stats"] = True
                selected_random_single_choice_questions = random.choices(selected_single_choice_questions_list, k=single_choice_question_num)
            else:
                selected_random_single_choice_questions = selected_single_choice_questions_list
            for item in selected_random_single_choice_questions:
                response["questions"].append({
                    "questionId": item.question_id,
                    "questionType": item.question_type,
                    "questionChapter": item.question_chapter,
                    "questionContent": item.question_content,
                    "questionChoiceAContent": item.question_choice_a_content,
                    "questionChoiceBContent": item.question_choice_b_content,
                    "questionChoiceCContent": item.question_choice_c_content,
                    "questionChoiceDContent": item.question_choice_d_content,
                    "questionAnswer": item.question_answer,
                })

        if multiple_choice_question_num != -1:
            all_multiple_choice_questions_queryset = MultipleChoiceQuestion.objects.all()
            for item in all_multiple_choice_questions_queryset:
                all_multiple_choice_questions_list.append(Question(item))
            selected_multiple_choice_questions_list = all_multiple_choice_questions_list
            if need_to_select_from_chapter:
                selected_multiple_choice_questions_list = []
                item: Question
                for item in all_multiple_choice_questions_list:
                    if chapter_start <= item.question_chapter <= chapter_end:
                        selected_multiple_choice_questions_list.append(item)
            if len(selected_multiple_choice_questions_list) >= multiple_choice_question_num:
                response["multiple_choice_question_stats"] = True
                selected_random_multiple_choice_questions = random.choices(selected_multiple_choice_questions_list, k=multiple_choice_question_num)
            else:
                selected_random_multiple_choice_questions = selected_multiple_choice_questions_list
            for item in selected_random_multiple_choice_questions:
                response["questions"].append({
                    "questionId": item.question_id,
                    "questionType": item.question_type,
                    "questionChapter": item.question_chapter,
                    "questionContent": item.question_content,
                    "questionChoiceAContent": item.question_choice_a_content,
                    "questionChoiceBContent": item.question_choice_b_content,
                    "questionChoiceCContent": item.question_choice_c_content,
                    "questionChoiceDContent": item.question_choice_d_content,
                    "questionAnswer": item.question_answer,
                })

        return Response(response)
# Contest question database ends
