from django.http.response import HttpResponseBadRequest
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view

from course_database.models import ExperimentCaseDatabase, CourseDocument, choiceMultipleQuestionDatabase, choiceSingleQuestionDatabase

import json
from enum import IntEnum


class QuestionType(IntEnum):
    SINGLE_CHOICE = 0
    MULTIPLE_CHOICE = 1


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


class CourseIdFileIdTemplate(APIView):

    def get(self, request, course_id, file_id, format=None):
        content = {
            "course_id": course_id,
            "file_id": file_id
        }
        return Response(content)


class ExperimentIdTemplate(APIView):

    def get(self, request, experiment_id, format=None):
        content = {
            "experiment_id": experiment_id,
        }
        return Response(content)


class ExperimentIdFileIdTemplate(APIView):

    def get(self, request, experiment_id, file_id, format=None):
        content = {
            "experiment_id": experiment_id,
            "file_id": file_id
        }
        return Response(content)


class QuestionTypeQuestionId(APIView):

    def get(self, request, question_type, question_id, format=None):
        content = {
            "question_type": question_type,
            "question_id": question_id
        }
        return Response(content)


class QuestionController(APIView):

    def get(self, request, format=None):
        all_single_choice_questions = choiceSingleQuestionDatabase.objects.all()
        all_multiple_choice_questions = choiceMultipleQuestionDatabase.objects.all()
        response = {
            "questions": []
        }

        for item in all_single_choice_questions:
            print("question content: " + item.question_content)
            response["questions"].append({
                "question_id": item.question_id,
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_chapter": item.question_chapter,
                "question_content": item.question_content,
                "question_choice_a_content": item.question_choice_a_content,
                "question_choice_b_content": item.question_choice_b_content,
                "question_choice_c_content": item.question_choice_c_content,
                "question_choice_d_content": item.question_choice_d_content,
                "question_answer": item.question_answer,
            })
        for item in all_multiple_choice_questions:
            print("question content: " + item.question_content)
            response["questions"].append({
                "question_id": item.question_id,
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "question_chapter": item.question_chapter,
                "question_content": item.question_content,
                "question_choice_a_content": item.question_choice_a_content,
                "question_choice_b_content": item.question_choice_b_content,
                "question_choice_c_content": item.question_choice_c_content,
                "question_choice_d_content": item.question_choice_d_content,
                "question_answer": item.question_answer,
            })
        # response = 'alive'
        # content = {
        #     "response": f"{response}"
        # }
        return Response(response)

    def post(self, request, format=None):
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)
        try:
            question_type = request_body["questionType"]
            if question_type == QuestionType.SINGLE_CHOICE:
                new_question = choiceSingleQuestionDatabase(
                    question_chapter=request_body["questionChapter"],
                    question_content=request_body["questionContent"],
                    question_choice_a_content=request_body["questionChoiceAContent"],
                    question_choice_b_content=request_body["questionChoiceBContent"],
                    question_choice_c_content=request_body["questionChoiceCContent"],
                    question_choice_d_content=request_body["questionChoiceDContent"],
                    question_answer=request_body["questionAnswer"],
                )
            elif question_type == QuestionType.MULTIPLE_CHOICE:
                new_question = choiceMultipleQuestionDatabase(
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
                    "question_type": "fuck you"
                }))
            new_question.save()
            return Response(request_body)
        except:
            return Response(dict({
                "msg": "Invaild question."
            }), status=400)


class QuestionCountController(APIView):

    def get(self, request, format=None):
        single_choice_questions_count = choiceSingleQuestionDatabase.objects.count()
        multiple_choice_questions_count = choiceMultipleQuestionDatabase.objects.count()
        question_count = single_choice_questions_count + multiple_choice_questions_count
        content = {
            "question_count": question_count
        }
        return Response(content)


class QuestionPutController(APIView):
    def put(self, request, question_type, question_id, format=None):
        request_body_unicode = request.body.decode('utf-8')
        request_body = json.loads(request_body_unicode)
        try:
            if question_type == QuestionType.SINGLE_CHOICE:
                old_question = choiceSingleQuestionDatabase.objects.get(question_id=question_id)
                old_question.question_chapter = request_body["questionChapter"]
                old_question.question_content = request_body["questionContent"]
                old_question.question_choice_a_content = request_body["questionChoiceAContent"]
                old_question.question_choice_b_content = request_body["questionChoiceBContent"]
                old_question.question_choice_c_content = request_body["questionChoiceCContent"]
                old_question.question_choice_d_content = request_body["questionChoiceDContent"]
                old_question.question_answer = request_body["questionAnswer"]

            elif question_type == QuestionType.MULTIPLE_CHOICE:
                old_question = choiceMultipleQuestionDatabase.objects.get(question_id=question_id)
                old_question.question_chapter = request_body["questionChapter"]
                old_question.question_content = request_body["questionContent"]
                old_question.question_choice_a_content = request_body["questionChoiceAContent"]
                old_question.question_choice_b_content = request_body["questionChoiceBContent"]
                old_question.question_choice_c_content = request_body["questionChoiceCContent"]
                old_question.question_choice_d_content = request_body["questionChoiceDContent"]
                old_question.question_answer = request_body["questionAnswer"]
            else:
                return Response(dict({
                    "question_type": "fuck you"
                }))
            old_question.save()
            return Response(request_body)
        except:
            return Response(dict({
                "msg": "Invaild question."
            }), status=400)
    def delete(self, request, question_type, question_id, format=None):
        try:
            if question_type == QuestionType.SINGLE_CHOICE:
                choiceSingleQuestionDatabase.objects.delete(question_id=question_id)
            elif question_type == QuestionType.MULTIPLE_CHOICE:
                choiceMultipleQuestionDatabase.objects.delete(question_id=question_id)
            else:
                return Response(dict({
                    "question_type": "fuck you"
                }))
            return Response("good")
        except:
            return Response(dict({
                "msg": "Delete invaild."
            }), status=400)
