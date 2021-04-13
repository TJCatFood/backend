from django.shortcuts import render
from django.db.models import F

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer, IntegerField, CharField, DateTimeField

from contest.serializer import ContestSerializer, ContestQuestionSerializer, MatchSerializer, AttendSerializer
from contest import models
from user.models import User
from course_database.models import SingleChoiceQuestion, MultipleChoiceQuestion
from course.models import Course
import datetime
import pytz
import json

utc = pytz.utc


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
                "matchId": match[0].match_id,
                "constestId": contest_id,
                "timeStamp": f"{match[0].timestamp}",
                "title": f"{contest.title}",
                "participantNumber": contest.participant_number,
                "startTime": f"{contest.start_time}",
                "endTime": f"{contest.end_time}",
                "chapter": contest.chapter,
                "description": f"{contest.description}",
                "rank": attend[0].rank,
                "score": attend[0].score,
                "courseId": contest.course_id_id,
                "publisherId": contest.publisher_id_id
            }
            response_list.append(item)
    return Response(response_list)


@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def get_match(request, match_id):
    try:
        match = models.Match.objects.get(pk=match_id)
    except models.Match.DoesNotExist:
        error = Error('Not Found: match not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        match.delete()
        return Response(match)

    params = request.query_params.dict()

    student_id = params.get('studentId', None)
    if student_id is None:
        error = Error('Bad Request: studentId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
    try:
        student_id = int(student_id)
    except TypeError:
        error = Error('Bad Request: studentId illegal!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    if match.user_id_id != student_id:
        error = Error('Bad Request: student have no access!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    contest_id = match.contest_id_id

    try:
        user = User.objects.get(pk=student_id)
        contest = models.Contest.objects.get(pk=contest_id)
    except models.Contest.DoesNotExist:
        error = Error('Not Found: user or contest not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    attend = models.AttendContest.objects.filter(user_id=student_id, contest_id=contest_id)
    if attend.count() <= 0:
        error = Error('Bad Request: The match is not over yet!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    question_and_answers = []
    questions = models.ContestQuestion.objects.filter(contest_id=contest_id)
    for q in questions:
        q_type = q.question_type
        q_id = q.question_id
        submission = models.ContestSubmission.objects.filter(contest_id=contest.contest_id, user_id=student_id, question_id=q_id, question_type=q_type)
        if submission.count() == 0:
            error = Error('Not Found: submission not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        answer = submission[0].answer
        if q_type == models.QuestionType.SINGLE:
            try:
                question = SingleChoiceQuestion.objects.get(pk=q_id)
            except SingleChoiceQuestion.DoesNotExist:
                error = Error('Not Found: question not found!')
                return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        elif q_type == models.QuestionType.MULTIPLE:
            try:
                question = MultipleChoiceQuestion.objects.get(pk=q_id)
            except MultipleChoiceQuestion.DoesNotExist:
                error = Error('Not Found: question not found!')
                return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        item = {
            "question": {
                "questionId": q_id,
                "questionType": q_type,
                "questionChapter": question.question_chapter,
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

    content = {
        "name": f"{user.realname}",
        "avatar": f"{user.avatar}",
        "userId": student_id,
        "contestId": contest_id,
        "courseId": contest.course_id_id,
        "timeStamp": f"{match.timestamp}",
        "title": f"{contest.title}",
        "publisherId": contest.publisher_id_id,
        "participantNumber": contest.participant_number,
        "startTime": f"{contest.start_time}",
        "endTime": f"{contest.end_time}",
        "chapter": contest.chapter,
        "description": f"{contest.description}",
        "rank": attend[0].rank,
        "score": attend[0].score,
        "questionAndAnswers": question_and_answers
    }
    return Response(content)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_matches_student(request):
    params = request.query_params
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

    try:
        student = User.objects.get(pk=student_id)
    except models.Contest.DoesNotExist:
        error = Error('Not Found: user not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    matches = []
    contests = models.Contest.objects.filter(course_id=course_id)
    for contest in contests:
        try:
            attend = models.AttendContest.objects.get(user_id=student_id, contest_id=contest.contest_id)
        except models.AttendContest.DoesNotExist:
            continue
        match = {
            "contestId": contest.contest_id,
            "timeStamp": f"{attend.timestamp}",
            "title": f"{contest.title}",
            "participantNumber": contest.participant_number,
            "startTime": f"{contest.start_time}",
            "endTime": f"{contest.end_time}",
            "chapter": contest.chapter,
            "description": f"{contest.description}",
            "rank": attend.rank,
            "score": attend.score,
            "courseId": contest.course_id_id,
            "publisherId": contest.publisher_id_id
        }
        matches.append(match)
    my_serializer = MatchContestSerializer(data=matches, many=True)
    my_serializer.is_valid(True)
    student = {
        "userId": student_id,
        "email": f"{student.email}",
        "name": f"{student.realname}",
        "avatar": f"{student.avatar}",
        "universityId": student.university_id_id,
        "schoolId": student.school_id_id,
        "personalId": student.personal_id
    }
    response = {
        "student": student,
        "matches": matches
    }
    return Response(response)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_matchid(request):
    params = request.query_params
    student_id = params.get('studentId', None)
    if student_id is None:
        error = Error('Bad Request: studentId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    contest_id = params.get('contestId', None)
    if contest_id is None:
        error = Error('Bad Request: contestId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    try:
        student_id = int(student_id)
        contest_id = int(contest_id)
    except TypeError:
        error = Error('Bad Request: studentId or contestId illegal!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    match = models.Match.objects.filter(contest_id=contest_id, user_id=student_id)
    attend = models.AttendContest.objects.filter(contest_id=contest_id, user_id=student_id)
    if match.count() > 0 and attend.count() == 0:
        return Response({
            "matchId": match[0].match_id,
            "timeStamp": f"{match[0].timestamp}"
        })
    else:
        error = Error('Not Found: match not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_contest_questions_student(request, contest_id):
    params = request.query_params
    student_id = params.get('studentId', None)
    if student_id is None:
        error = Error('Bad Request: studentId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    try:
        student_id = int(student_id)
    except TypeError:
        error = Error('Bad Request: studentId illegal!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = User.objects.get(pk=student_id)
    except User.DoesNotExist:
        error = Error('Not Found: user not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    try:
        contest = models.Contest.objects.get(pk=contest_id)
    except models.Contest.DoesNotExist:
        error = Error('Not Found: contest not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    match = models.Match.objects.filter(contest_id=contest_id, user_id=student_id)
    attend = models.AttendContest.objects.filter(contest_id=contest_id, user_id=student_id)
    if match.count() == 0:
        error = Error('Bad Request: student not in the contest!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
    if attend.count() > 0:
        error = Error('Bad Request: the student have already taken part in the contest!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    contest_questions = models.ContestQuestion.objects.filter(contest_id=contest_id).values()
    for contest_question in contest_questions:
        q_type = contest_question['question_type']
        q_id = contest_question['question_id']
        if q_type == models.QuestionType.SINGLE:
            question = SingleChoiceQuestion.objects.get(pk=q_id)
        elif q_type == models.QuestionType.MULTIPLE:
            question = MultipleChoiceQuestion.objects.get(pk=q_id)
        contest_question['question_chapter'] = question.question_chapter
        contest_question['question_content'] = question.question_content
        contest_question['question_choice_a_content'] = question.question_choice_a_content
        contest_question['question_choice_b_content'] = question.question_choice_b_content
        contest_question['question_choice_c_content'] = question.question_choice_c_content
        contest_question['question_choice_d_content'] = question.question_choice_d_content
    contest_questions = list(contest_questions)
    my_serializer = QuestionSerializer(data=contest_questions, many=True)
    my_serializer.is_valid(True)
    return Response({
        "questions": my_serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_contest_questions_teacher(request, contest_id):
    params = request.query_params
    user_id = params.get('userId', None)
    if user_id is None:
        error = Error('Bad Request: userId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = int(user_id)
    except TypeError:
        error = Error('Bad Request: userId illegal!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        error = Error('Not Found: user not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    try:
        contest = models.Contest.objects.get(pk=contest_id)
    except models.Contest.DoesNotExist:
        error = Error('Not Found: contest not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    contest_questions = models.ContestQuestion.objects.filter(contest_id=contest_id).values()
    for contest_question in contest_questions:
        q_type = contest_question['question_type']
        q_id = contest_question['question_id']
        if q_type == models.QuestionType.SINGLE:
            question = SingleChoiceQuestion.objects.get(pk=q_id)
        elif q_type == models.QuestionType.MULTIPLE:
            question = MultipleChoiceQuestion.objects.get(pk=q_id)
        contest_question['question_chapter'] = question.question_chapter
        contest_question['question_content'] = question.question_content
        contest_question['question_answer'] = question.question_answer
        contest_question['question_choice_a_content'] = question.question_choice_a_content
        contest_question['question_choice_b_content'] = question.question_choice_b_content
        contest_question['question_choice_c_content'] = question.question_choice_c_content
        contest_question['question_choice_d_content'] = question.question_choice_d_content
    contest_questions = list(contest_questions)
    my_serializer = QuestionAnswerSerializer(data=contest_questions, many=True)
    my_serializer.is_valid(True)
    return Response({
        "questions": my_serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_contest_end(request):
    params = request.query_params.dict()
    course_id = params.get('courseId', None)
    if course_id is None:
        error = Error('Bad Request: courseId needed!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    try:
        course_id = int(course_id)
    except TypeError:
        error = Error('Bad Request: courseId illegal!')
        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        error = Error('Not Found: course not found!')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)

    contests = models.Contest.objects.filter(course_id=course_id).order_by(F('end_time').desc())
    contests = list(contests.values())
    time = utc.localize(datetime.datetime.utcnow())
    if len(contests) > 0 and time <= contests[0]['end_time']:
        contests = contests[1:len(contests)]
    serializer = FKContestSerializer(data=contests, many=True)
    serializer.is_valid(True)
    return Response({
        "contests": serializer.data
    })


class MatchView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        matches = models.Match.objects.all()
        match_serializer = MatchSerializer(matches, many=True)
        return Response(match_serializer.data)

    def post(self, request, format=None):
        data = request.data
        match_serializer = MatchSerializer(data=data)
        match_serializer.is_valid(True)
        match_serializer.save()
        return Response(match_serializer.data)

    def delete(self, request, format=None):
        params = request.query_params.dict()
        user_id = params.get('userId', None)
        contest_id = params.get('contestId', None)
        match = models.Match.objects.get(user_id=user_id, contest_id=contest_id).delete()
        return Response(match)


class AttendView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        attends = models.AttendContest.objects.all()
        attend_serializer = AttendSerializer(attends, many=True)
        return Response(attend_serializer.data)

    def post(self, request, format=None):
        data = request.data
        attend_serializer = AttendSerializer(data=data)
        attend_serializer.is_valid(True)
        attend_serializer.save()
        return Response(attend_serializer.data)

    def delete(self, request, format=None):
        params = request.query_params.dict()
        user_id = params.get('userId', None)
        contest_id = params.get('contestId', None)
        attend = models.AttendContest.objects.get(user_id=user_id, contest_id=contest_id).delete()
        return Response(attend)


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
        params = request.query_params.dict()
        user_id = params.get('userId', None)
        if user_id is None:
            error = Error('Bad Request: userId needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        course_id = params.get('courseId', None)
        if course_id is None:
            error = Error('Bad Request: courseId needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = int(user_id)
            course_id = int(course_id)
        except TypeError:
            error = Error('Bad Request: studentId or courseId illegal!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        contests = models.Contest.objects.filter(course_id=course_id).order_by(F('end_time').desc())
        if contests.count() == 0:
            return Response([])
        time = utc.localize(datetime.datetime.utcnow())
        if time > contests[0].end_time:
            return Response([])
        contest = contests[0]
        serializer = ContestSerializer(contest)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            error = Error('Not Found: user not found')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if user.character == 4:
            submission = models.ContestSubmission.objects.filter(contest_id=contest.contest_id, user_id=user_id)
            if submission.count() == 0:
                b_is_participated = False
                try:
                    match = models.Match.objects.get(contest_id=contest.contest_id, user_id=user_id)
                except models.Match.DoesNotExist:
                    b_is_participating = False
                else:
                    b_is_participating = True
            else:
                b_is_participated = True
                b_is_participating = False
        else:
            b_is_participated = False
            b_is_participating = False
        contest_data = dict(serializer.data)
        return Response({
            "contest": contest_data,
            "bIsParticipated": b_is_participated,
            "bIsParticipating": b_is_participating
        })

    def post(self, request, format=None):
        data = request.data
        contest = data.get('contest', None)
        if contest is None:
            error = Error('Bad Request: contest needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        questions = contest.get('questions', None)
        if questions is None:
            error = Error('Bad Request: questions needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        try:
            questions = list(questions)
        except TypeError:
            error = Error('Bad Request: questions must be a list!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        length = len(questions)
        for i in range(length):
            for j in range(length):
                if i == j:
                    continue
                else:
                    if questions[i] == questions[j]:
                        error = Error('Bad Request: question duplication is not allowed!')
                        return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        contest_serializer = ContestSerializer(data=contest)
        if not contest_serializer.is_valid():
            error = Error('Bad Request: contest illegal!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        contest_serializer.save()
        contest_id = contest_serializer.data.get('contest_id', None)

        for question in questions:
            question['contest_id'] = contest_id
            q_type = question.get('question_type', None)
            q_id = question.get('question_id', None)
            if q_type is None or q_id is None:
                models.Contest.objects.get(pk=contest_id).delete()
                error = Error('Bad Request: question_type and question_id needed!')
                return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
            if not self.check_question(q_type, q_id):
                models.Contest.objects.get(pk=contest_id).delete()
                error = Error('Not Found: question not found!')
                return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        question_serializer = ContestQuestionSerializer(data=questions, many=True)
        if not question_serializer.is_valid():
            models.Contest.objects.get(pk=contest_id).delete()
            error = Error('Bad Request: question illegal!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        question_serializer.save()

        contest_questions = models.ContestQuestion.objects.filter(contest_id=contest_id).values()
        for contest_question in contest_questions:
            q_type = contest_question['question_type']
            q_id = contest_question['question_id']
            if q_type == models.QuestionType.SINGLE:
                question = SingleChoiceQuestion.objects.get(pk=q_id)
            elif q_type == models.QuestionType.MULTIPLE:
                question = MultipleChoiceQuestion.objects.get(pk=q_id)
            contest_question['question_chapter'] = question.question_chapter
            contest_question['question_content'] = question.question_content
            contest_question['question_answer'] = question.question_answer
            contest_question['question_choice_a_content'] = question.question_choice_a_content
            contest_question['question_choice_b_content'] = question.question_choice_b_content
            contest_question['question_choice_c_content'] = question.question_choice_c_content
            contest_question['question_choice_d_content'] = question.question_choice_d_content
        contest_questions = list(contest_questions)
        my_serializer = QuestionAnswerSerializer(data=contest_questions, many=True)
        my_serializer.is_valid(True)
        response = {
            "contest": contest_serializer.data,
            "questions": []
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def delete(self, request, format=None):
        params = request.query_params.dict()
        contest_id = params['contestId']
        models.Contest.objects.get(pk=contest_id).delete()
        return Response()

    def check_question(self, q_type, q_id):
        if q_type == models.QuestionType.SINGLE:
            try:
                question = SingleChoiceQuestion.objects.get(pk=q_id)
            except SingleChoiceQuestion.DoesNotExist:
                return False
        elif q_type == models.QuestionType.MULTIPLE:
            try:
                question = MultipleChoiceQuestion.objects.get(pk=q_id)
            except MultipleChoiceQuestion.DoesNotExist:
                return False
        return True


class MatchesView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, contest_id, format=None):
        params = request.query_params.dict()

        pg_num = params.get('pageNum', None)
        if pg_num is None:
            error = Error('Bad Request: pageNum needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        pg_sz = params.get('pageSize', None)
        if pg_sz is None:
            error = Error('Bad Request: pageSize needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        try:
            pg_num = int(pg_num)
            pg_sz = int(pg_sz)
        except TypeError:
            error = Error('Bad Request: pageNum or pageSize illegal!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            contest = models.Contest.objects.get(pk=contest_id)
        except models.Contest.DoesNotExist:
            error = Error('Not Found: contest not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        return self.get_contest_matches(contest, pg_sz, pg_num)

    def get_contest_matches(self, contest, pg_sz, pg_num):
        all_matches = models.Match.objects.filter(contest_id=contest.contest_id).order_by('match_tag').distinct('match_tag')
        total = all_matches.count()
        pg_start = (pg_num - 1) * pg_sz
        pg_end = pg_num * pg_sz
        if pg_end > total:
            pg_end = total
        if pg_start >= total:
            all_matches = []
        else:
            all_matches = all_matches[pg_start:pg_end]
        matches = []

        for match in all_matches:
            tag_matches = models.Match.objects.filter(match_tag=match.match_tag)
            participants = []
            for tag_match in tag_matches:
                participant = User.objects.get(pk=tag_match.user_id_id)
                attend = models.AttendContest.objects.get(contest_id=contest.contest_id, user_id=tag_match.user_id_id)
                item = {
                    "userId": participant.user_id,
                    "email": f"{participant.email}",
                    "name": f"{participant.realname}",
                    "avatar": f"{participant.avatar}",
                    "universityId": participant.university_id_id,
                    "schoolId": participant.school_id_id,
                    "rank": attend.rank,
                    "score": attend.score,
                    "personalId": participant.personal_id
                }
                participants.append(item)
            matches.append({
                "matchTag": match.match_tag,
                "timeStamp": f"{match.timestamp}",
                "participants": participants
            })

        response = {
            "contestId": contest.contest_id,
            "publisherId": contest.publisher_id_id,
            "title": f"{contest.title}",
            "participantNumber": contest.participant_number,
            "startTime": f"{contest.start_time}",
            "endTime": f"{contest.end_time}",
            "chapter": contest.chapter,
            "description": f"{contest.description}",
            "courseId": contest.course_id_id,
            "matches": matches,
            "pagination": {
                "pageNum": pg_num,
                "pageSize": pg_sz,
                "total": total
            }
        }
        return Response(response)


class Error():

    def __init__(self, msg):
        self.error = {
            "error": {
                "message": f"{msg}"
            }
        }


class QuestionAnswerSerializer(Serializer):
    question_id = IntegerField()
    question_type = IntegerField()
    question_chapter = IntegerField()
    question_content = CharField()
    question_answer = CharField()
    question_choice_a_content = CharField()
    question_choice_b_content = CharField()
    question_choice_c_content = CharField()
    question_choice_d_content = CharField()


class QuestionSerializer(Serializer):
    question_id = IntegerField()
    question_type = IntegerField()
    question_chapter = IntegerField()
    question_content = CharField()
    question_choice_a_content = CharField()
    question_choice_b_content = CharField()
    question_choice_c_content = CharField()
    question_choice_d_content = CharField()


class MatchContestSerializer(Serializer):
    contestId = IntegerField()
    timeStamp = CharField()
    title = CharField()
    participantNumber = IntegerField()
    startTime = CharField()
    endTime = CharField()
    chapter = IntegerField()
    description = CharField()
    rank = IntegerField()
    score = IntegerField()
    courseId = IntegerField()
    publisherId = IntegerField()


class FKContestSerializer(Serializer):
    contest_id = IntegerField()
    course_id_id = IntegerField()
    publisher_id_id = IntegerField()
    title = CharField()
    participant_number = IntegerField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    chapter = IntegerField()
    description = CharField()
