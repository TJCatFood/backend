from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny

from contest.serializer import ContestSerializer
from contest import models
from user.models import User
from course_database.models import SingleChoiceQuestion, MultipleChoiceQuestion


@api_view(['GET'])
@permission_classes([AllowAny])
def get_matches(request):
    params = request.query_params.dict()

    student_id = params.get('studentId', None)
    if student_id is None:
        error = Error('Bad Request: studentId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    course_id = params.get('courseId', None)
    if course_id is None:
        error = Error('Bad Request: courseId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        student_id = int(student_id)
        course_id = int(course_id)
    except TypeError:
        error = Error('Bad Request: studentId or courseId illegal!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    response_list = []
    contests = models.Contest.objects.filter(course_id=course_id)

    for contest in contests:
        contest_id = contest.contest_id
        match = models.Match.objects.filter(user_id=student_id, contest_id=contest_id)
        attend = models.AttendContest.objects.filter(user_id=student_id, contest_id=contest_id)
        if match.count() > 0 and attend.count() > 0:
            item = {
                "matchId": f"{match[0].match_id}",
                "constestId": f"{contest_id}",
                "timeStamp": f"{match[0].timestamp}",
                "title": f"{contest.title}",
                "participantNumber": f"{contest.participant_number}",
                "startTime": f"{contest.start_time}",
                "endTime": f"{contest.end_time}",
                "chapter": f"{contest.chapter}",
                "description": f"{contest.description}",
                "rank": f"{attend[0].rank}",
                "score": f"{attend[0].score}",
                "courseId": f"{contest.course_id}",
                "publisherId": f"{contest.publisher_id}"
            }
            response_list.append(item)

    return Response(response_list)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_match(request, match_id):
    try:
        match = models.Match.objects.get(pk=match_id)
    except:
        error = Error('Not Found: match not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)
    
    user_id = match.user_id
    contest_id = match.contest_id

    try:
        user = User.objects.get(pk=user_id)
        contest = models.Contest.objects.get(pk=contest_id)
    except:
        error = Error('Not Found: user or contest not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    attend = models.AttendContest.objects.filter(user_id=student_id, contest_id=contest_id)
    if attend.count <= 0:
        error = Error('Bad Request: The match is not over yet!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
    
    question_and_answers = []
    questions = models.ContestQuestion.objects.filter(contest_id=contest_id)
    for q in questions:
        q_type = q.question_type
        q_id = q.question_id
        try:
            submission = models.ContestSubmission.objects.get(contest_id=contest_id, 
            user_id=user_id, question_id=q_type, question_type=q_type)
        except models.ContestSubmission.DoesNotExist:
            error = Error('Not Found: submission not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        answer = submission.answer
        if q_type == models.QuestionType.SINGLE:
            try:
                question = SingleChoiceQuestion.objects.get(pk = q_id)
            except SingleChoiceQuestion.DoesNotExist:
                error = Error('Not Found: question not found!')
                return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        elif q_type == models.QuestionType.MULTIPLE:
            try:
                question = MultipleChoiceQuestion.objects.get(pk = q_id)
            except MultipleChoiceQuestion.DoesNotExist:
                error = Error('Not Found: question not found!')
                return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        item = {
            "question": {
                "questionId": f"{q_id}",
                "questionType": f"{q_type}",
                "questionChapter": f"{question.question_chapter}",
                "questionContent": f"{question.question_content}",
                "questionAnswer": f"{question.question_answer}",
                "questionChoiceAContent": f"{question.question_choice_a_content}",
                "questionChoiceBContent": f"{question.question_choice_b_content}",
                "questionChoiceCContent": f"{question.question_choice_c_content}",
                "questionChoiceDContent": f"{question.question_choice_d_content}"
            },
            "answer": f"{answer}"
        }
        question_and_answers.append(item)

    # matches = models.Match.objects.filter(match_tag=match.match_tag)
    # participants = []
    # for match in matches:
    #     participant = User.objects.filter(user_id=match.user_id)
    #     item = {
    #         "userId": user_id,
    #         "nickname": participant.name,
    #         "avatar": "string",
    #         "rank": 0
    #     }

    content = {
        "name": f"{user.realname}",
        "avatar": f"{user.avatar}",
        "userId": f"{user_id}",
        "contestId": f"{contest_id}",
        "courseId": f"{contest.course_id}",
        "timeStamp": f"{match.timestamp}",
        "title": f"{contest.title}",
        "publisherId": f"{contest.publisher_id}",
        "participantNumber": f"{contest.participant_number}",
        "startTime": f"{contest.start_time}",
        "endTime": f"{contest.end_time}",
        "chapter": f"{contest.chapter}",
        "description": f"{contest.description}",
        "rank": f"{attend[0].rank}",
        "score": f"{attend[0].score}",
        "questionAndAnswers": f"{question_and_answers}"
    }
    return Response(content)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_matches_student(request):
    params = request.query_params
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_matchid(request):
    params = request.query_params
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_contest_questions(request, contest_id):
    params = request.query_params
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_contest_end(request):
    params = request.query_params
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


class TestView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response(content)


class ContestView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        contests = models.Contest.objects.all()
        serializer = ContestSerializer(contests, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        serializer = ContestSerializer(data=data['contest'])
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MatchesView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, contest_id, format=None):
        params = request.query_params.dict()
        return self.get_contest_matches(contest_id)

    def get_contest_matches(self, contest_id):
        content = {
            "contestId": f"{contest_id}",
            "response": 'get_contest_matches test succeed'
        }
        return Response(content)


class Error():
    
    def __init__(self, msg):
        self.error = {
            "error": {
                "message": f"{msg}"
            }
        }
