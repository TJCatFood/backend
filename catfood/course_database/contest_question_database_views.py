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

        all_questions = []
        if need_filter:
            if requested_question_type == QuestionType.SINGLE_CHOICE:
                all_single_choice_questions = SingleChoiceQuestion.objects.all()
                for item in all_single_choice_questions:
                    all_questions.append(Question(item))
            elif requested_question_type == QuestionType.MULTIPLE_CHOICE:
                all_multiple_choice_questions = MultipleChoiceQuestion.objects.all()
                for item in all_multiple_choice_questions:
                    all_questions.append(Question(item))
            else:
                return Response(dict({
                    "msg": "question_type wants to fuck you"
                }), status=400)
        else:
            all_single_choice_questions = SingleChoiceQuestion.objects.all()
            for item in all_single_choice_questions:
                all_questions.append(Question(item))
            all_multiple_choice_questions = MultipleChoiceQuestion.objects.all()
            for item in all_multiple_choice_questions:
                all_questions.append(Question(item))

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
# Contest question database ends
