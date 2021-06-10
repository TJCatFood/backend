from django.shortcuts import render
from django.db.models import F

from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from match.room import Room, RoomStatus, ContestRooms
from contest.serializer import SubmissionSerializer, MatchSerializer, AttendSerializer
from contest.models import Contest, Match, ContestSubmission, Contest, ContestQuestion, QuestionType
from course_database.models import SingleChoiceQuestion, MultipleChoiceQuestion
from user.models import User
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher
import time
from threading import Timer
import requests
import json
import datetime
import pytz

utc = pytz.utc
# {channel_id, room}
rooms = {}
# {contest_id, contest_rooms(start_rooms, wait_rooms)}
contests = {}
ws_url = "http://nchan:8081/api/v1/contest/pub?id="
room_time = 15.0
cache_time = 300
ws_time = 2.0
contest_time = 180
submit_wait_time = 10.0
rank_bonus = 10


def contest_start(room):
    channel_id = room.channel_id
    contest_id = room.contest_id
    matches = Match.objects.all().order_by(F('match_tag').desc())
    if matches.count() == 0:
        match_tag = 1
    else:
        match_tag = matches[0].match_tag + 1
    matches = []
    user_id_list = room.user_id_list
    for user_id in user_id_list:
        match = {
            'contest_id': contest_id,
            'user_id': user_id,
            'match_tag': match_tag
        }
        matches.append(match)
    match_serializer = MatchSerializer(data=matches, many=True)
    match_serializer.is_valid(True)
    match_serializer.save()


def check_room(channel_id):
    if channel_id in rooms:
        room = rooms[channel_id]
        if not room.bis_end():
            url = ws_url + str(channel_id)
            payload = json.dumps({
                "type": 6,
                "content": "Time out! Please submit!",
            })
            requests.post(url, data=payload)
            timer = Timer(submit_wait_time, contest_end, (room,))
            timer.start()


def contest_end(room):
    # results = [[rank_list],[score_list]]
    results = calculate_score(room)
    ranks = results[0]
    scores = results[1]
    channel_id = room.channel_id
    url = ws_url + str(channel_id)
    payload = json.dumps({
        "type": 7,
        "content": "contest end!",
        "rankArray": ranks,
        "scoreArray": scores
    })
    requests.post(url, data=payload)

    contest_id = room.contest_id
    user_id_list = room.user_id_list
    attends = []
    for i in range(room.total_count):
        user_id = user_id_list[i]
        try:
            match = Match.objects.get(user_id=user_id, contest_id=contest_id)
        except Match.DoesNotExist:
            error = Error('Not Found: match not found')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        attend = {
            'user_id': user_id,
            'contest_id': contest_id,
            'timestamp': match.timestamp,
            'score': scores[i],
            'rank': ranks[i]
        }
        attends.append(attend)
    attend_serializer = AttendSerializer(data=attends, many=True)
    attend_serializer.is_valid(True)
    attend_serializer.save()
    delete_room(room)


def delete_room(room):
    del rooms[room.channel_id]
    contests[room.contest_id].start_rooms.remove(room)


def calculate_score(room):
    contest_id = room.contest_id
    user_id_list = room.user_id_list
    score_list = []
    time_list = []
    try:
        contest = Contest.objects.get(contest_id=contest_id)
    except Contest.DoesNotExist:
        error = Error('Not Found: contest not found')
        return Response(error.error, status=status.HTTP_404_NOT_FOUND)
    questions = ContestQuestion.objects.filter(contest_id=contest_id)
    count = questions.count()
    for user_id in user_id_list:
        submissions = ContestSubmission.objects.filter(user_id=user_id, contest_id=contest_id)
        right_count = 0
        for submission in submissions:
            q_id = submission.question_id
            q_type = submission.question_type
            answer = submission.answer
            right_count += question_check(q_id, q_type, answer)
        if submissions.count() > 0:
            time_list.append(submissions[0].timestamp)
        else:
            time_list.append(utc.localize(datetime.datetime.utcnow()))
        score_list.append(right_count * 100 / count)
    rank_list = calculate_rank(score_list, time_list)
    for i in range(len(rank_list)):
        if rank_list[i] == 1:
            score_list[i] += rank_bonus
            break
    return [rank_list, score_list]


def calculate_rank(score_list, time_list):
    rank_list = []
    length = len(score_list)
    for i in range(length):
        score = score_list[i]
        cnt = 0
        for j in range(length):
            if score_list[j] > score or (score_list[j] == score and time_list[j] < time_list[i]):
                cnt += 1
        rank_list.append(cnt + 1)
    return rank_list


def question_check(q_id, q_type, answer):
    if q_type == QuestionType.SINGLE:
        question = SingleChoiceQuestion.objects.get(pk=q_id)
    elif q_type == QuestionType.MULTIPLE:
        question = MultipleChoiceQuestion.objects.get(pk=q_id)
    corr_ans = "".join(sorted(question.question_answer))
    answer_list = sorted(answer)
    answer = "".join(answer_list)
    if answer.lower() == corr_ans.lower():
        return 1
    else:
        return 0


class TestView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        room = Room(None, 3, 0)
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response({"channel_id": f"{room.channel_id}"})


class StartView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent]

    def post(self, request, format=None):
        data = request.data
        if 'student_id' in data:
            student_id = data['student_id']
        else:
            error = Error('Bad Request: student_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        if 'contest_id' in data:
            contest_id = data['contest_id']
        else:
            error = Error('Bad Request: contest_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            contest = Contest.objects.get(pk=contest_id)
        except Contest.DoesNotExist:
            error = Error('Not Found: contest not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        match = Match.objects.filter(user_id=student_id, contest_id=contest_id)
        if match.count() > 0:
            error = Error('Bad Request: Students have already taken part in the contest!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            error = Error('Not Found: student not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if cache.get(student_id) is not None:
            # error = Error('Bad Request: User has already matched!')
            # return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
            channel_id = cache.get(student_id)
            return Response({"channel_id": f"{channel_id}"})

        if contest_id not in contests:
            contest_rooms = ContestRooms()
            contests[contest_id] = contest_rooms
        else:
            contest_rooms = contests[contest_id]

        rooms_queue = contest_rooms.wait_rooms
        if rooms_queue.empty():
            room = self.create_room(student_id, contest)
        else:
            room = self.choose_room(student_id, contest)
        cache.set(student_id, room.channel_id, cache_time)
        return Response({"channel_id": f"{room.channel_id}"})

    def create_room(self, user_id, contest):
        room_queue = contests[contest.contest_id].wait_rooms
        room = Room(user_id, contest.participant_number, contest.contest_id)
        rooms[room.channel_id] = room
        room_queue.put(room)
        return room

    def choose_room(self, user_id, contest):
        room_queue = contests[contest.contest_id].wait_rooms
        while (room_queue.empty() is False):
            room = room_queue.queue[0]
            if room.bis_empty():
                room_queue.get()
                continue
            else:
                room.add_user(user_id)
                if room.bis_full():
                    room_queue.get()
                    room.set_status(RoomStatus.READY)
                    timer = Timer(ws_time, self.room_ready, (room,))
                    timer.start()
                return room
        else:
            return self.create_room(user_id, contest)

    def room_ready(self, room):
        channel_id = room.channel_id
        url = ws_url + str(channel_id)
        payload = json.dumps({
            "type": 1,
            "content": "request ready!"
        })
        requests.post(url, data=payload)
        timer = Timer(room_time, self.room_check_ready, (room,))
        timer.start()

    def room_check_ready(self, room):
        if room.bis_all_ready():
            return
        else:
            self.room_clear(room)

    def room_clear(self, room):
        sz = room.total_count
        ready_list = room.ready_list
        del_cnt = 0
        for i in range(sz):
            if ready_list[i] is False:
                user_id = room.delete_user_index(i - del_cnt)
                del_cnt += 1
                cache.delete(user_id)
        room.clear_ready()
        room.set_status(RoomStatus.WAIT)
        contest_rooms = contests[room.contest_id]
        contest_rooms.wait_rooms.put(room)
        channel_id = room.channel_id
        url = ws_url + str(channel_id)
        payload = json.dumps({
            "type": 2,
            "content": "room clear!"
        })
        requests.post(url, data=payload)


class CancelView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent]

    def post(self, request, format=None):
        data = request.data
        if 'student_id' in data:
            student_id = data['student_id']
        else:
            error = Error('Bad Request: student_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        if 'channel_id' in data:
            channel_id = data['channel_id']
        else:
            error = Error('Bad Request: channle_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            error = Error('Not Found: student not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if channel_id in rooms:
            room = rooms[channel_id]
        else:
            error = Error('Not Found: room not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if room.get_user_index(student_id) < 0:
            error = Error('Not Found: user not in room!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if room.status == RoomStatus.READY:
            error = Error('Bad Request: Cannot cancel for the matched room!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        cache.delete(student_id)
        room.delete_user(student_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IndexView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent]

    def get(sele, request, format=None):
        data = request.query_params.dict()
        if 'studentId' in data:
            student_id = data['studentId']
        else:
            error = Error('Bad Request: student_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        if 'channelId' in data:
            channel_id = data['channelId']
        else:
            error = Error('Bad Request: channel_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_id = int(student_id)
        except TypeError:
            error = Error('Bad Request: student_id illegal!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            error = Error('Not Found: student not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if channel_id in rooms:
            room = rooms[channel_id]
        else:
            error = Error('Not Found: room not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        index = room.get_user_index(student_id)
        if index >= 0:
            return Response({"index": index})
        else:
            error = Error('Not Found: student not in room!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)


class ReadyView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent]

    def post(self, request, format=None):
        data = request.data
        if 'student_id' in data:
            student_id = data['student_id']
        else:
            error = Error('Bad Request: student_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        if 'channel_id' in data:
            channel_id = data['channel_id']
        else:
            error = Error('Bad Request: channel_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        if 'status' in data:
            ready_status = data['status']
            if not isinstance(ready_status, bool):
                error = Error('Bad Request: status illegal!')
                return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        else:
            error = Error('Bad Request: status needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            error = Error('Not Found: student not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if channel_id in rooms:
            room = rooms[channel_id]
        else:
            error = Error('Not Found: room not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if room.status != RoomStatus.READY:
            error = Error('Bad Request: Cannot prepare for the room!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        if ready_status is False:
            self.room_clear(room)
        else:
            res = room.user_ready(student_id)
            if res is None:
                error = Error('Not Found: student not in room!')
                return Response(error.error, status=status.HTTP_404_NOT_FOUND)
            if res == -1:
                error = Error('Bad Request: The user has already ready!')
                return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
            if room.bis_all_ready():
                self.all_ready(room)
            else:
                channel_id = room.channel_id
                url = ws_url + str(channel_id)
                payload = json.dumps({
                    "type": 3,
                    "content": "A user ready!",
                    "readyArray": room.ready_list
                })
                requests.post(url, data=payload)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def room_clear(self, room):
        sz = room.total_count
        ready_list = room.ready_list
        del_cnt = 0
        for i in range(sz):
            if ready_list[i] is False:
                user_id = room.delete_user_index(i - del_cnt)
                del_cnt += 1
                cache.delete(user_id)
        room.clear_ready()
        room.set_status(RoomStatus.WAIT)
        contest_rooms = contests[room.contest_id]
        contest_rooms.wait_rooms.put(room)
        channel_id = room.channel_id
        url = ws_url + str(channel_id)
        payload = json.dumps({
            "type": 2,
            "content": "room clear!"
        })
        requests.post(url, data=payload)

    def all_ready(self, room):
        room.set_status(RoomStatus.START)
        contest_rooms = contests[room.contest_id]
        contest_rooms.start_rooms.append(room)
        channel_id = room.channel_id
        url = ws_url + str(channel_id)
        payload = json.dumps({
            "type": 4,
            "content": "Contest start!",
        })
        contest_start(room)
        requests.post(url, data=payload)
        timer = Timer(contest_time, check_room, (channel_id,))
        timer.start()


class ChannelView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent]

    def get(sele, request, format=None):
        data = request.query_params.dict()
        if 'studentId' in data:
            student_id = data['studentId']
        else:
            error = Error('Bad Request: student_id needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_id = int(student_id)
        except TypeError:
            error = Error('Bad Request: student_id illegal!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            error = Error('Not Found: student not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        channel_id = cache.get(student_id)
        if channel_id is None:
            error = Error('Not Found: student not in room!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"channelId": f"{channel_id}"})


class SubmissionView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent]

    def post(self, request, format=None):
        data = request.data

        student_id = data.get('student_id', None)
        channel_id = data.get('channel_id', None)
        answers = data.get('answers', None)
        if student_id is None or channel_id is None or answers is None:
            error = Error('Bad Request: student_id, channel_id and answers needed!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        try:
            student_id = int(student_id)
            answers = list(answers)
        except TypeError:
            error = Error('Bad Request: student_id or answers illegal!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        if channel_id in rooms:
            room = rooms[channel_id]
        else:
            error = Error('Not Found: room not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        submissions = []
        for answer in answers:
            q_id = answer.get('question_id', None)
            q_type = answer.get('question_type', None)
            ans = answer.get('answer', None)
            if q_id is None or q_type is None or ans is None:
                error = Error('Bad Request: question_id, question_type and answer needed!')
                return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
            submission = {
                'user_id': student_id,
                'contest_id': rooms[channel_id].contest_id,
                'question_id': q_id,
                'question_type': q_type,
                'answer': ans
            }
            submissions.append(submission)
        sub_serailizer = SubmissionSerializer(data=submissions, many=True)
        sub_serailizer.is_valid(True)
        sub_serailizer.save()

        res = room.user_submit(student_id)
        if res is None:
            error = Error('Not Found: student not in room!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)
        if res == -1:
            error = Error('Bad Request: The user has already submitted!')
            return Response(error.error, status=status.HTTP_400_BAD_REQUEST)
        if room.bis_end():
            contest_end(room)
        else:
            url = ws_url + str(channel_id)
            payload = json.dumps({
                "type": 5,
                "content": "user " + str(res) + "submit!",
                "submitIndex": res
            })
            requests.post(url, data=payload)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Error():

    def __init__(self, msg):
        self.error = {
            "error": {
                "message": f"{msg}"
            }
        }
