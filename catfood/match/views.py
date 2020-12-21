from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.core.cache import cache

from match.room import Room, RoomStatus, ContestRooms
from contest.models import Contest
from user.models import User
import time
from threading import Timer
import requests
import json


rooms = {}
contests = {}
ws_url = "http://nchan:8081/api/v1/contest/pub?id="
room_time = 60.0
cache_time = 600


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
    permission_classes = (AllowAny,)

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

        try:
            user = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            error = Error('Not Found: student not found!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)

        if cache.get(student_id) is not None:
            return Response('User has already matched!')

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
                    self.room_ready(room)
                return room
        else:
            return self.create_room(user_id, contest)

    def room_ready(self, room):
        channel_id = room.channel_id
        time.sleep(1)
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
    permission_classes = (AllowAny,)

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

        cache.delete(student_id)
        room.delete_user(student_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IndexView(APIView):
    permission_classes = (AllowAny,)

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
            return Response({"index": f"{index}"})
        else:
            error = Error('Not Found: student not in room!')
            return Response(error.error, status=status.HTTP_404_NOT_FOUND)


class ReadyView(APIView):
    permission_classes = (AllowAny,)

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
                    "readyArray": f"{room.ready_list}"
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
        match_id = self.contest_start(room)
        channel_id = room.channel_id
        url = ws_url + str(channel_id)
        payload = json.dumps({
            "type": 4,
            "content": "Contest start!",
            "matchId": f"{match_id}"
            })
        requests.post(url, data=payload)

    def contest_start(self, room):
        return 1


class ChannelView(APIView):
    permission_classes = (AllowAny,)

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


class Error():

    def __init__(self, msg):
        self.error = {
            "error": {
                "message": f"{msg}"
            }
        }
