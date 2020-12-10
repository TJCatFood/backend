from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
              
from match.room import Room, RoomStatus, ContestRooms
from contest.models import Contest
from user.models import User
import time
from threading import Timer
import requests


rooms = {}
contests = {}
ws_url = ""


class TestView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        room = Room(None, 3)
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response(content)


class StartView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        data = request.data
        if 'studentId' in data:
            student_id = data['studentId']
        else:
            return Response('bad request1')

        if 'contestId' in data:
            contest_id = data['contestId']
        else:
            return Response('bad request2')

        try:
            contest = Contest.objects.get(pk = contest_id)
        except Contest.DoesNotExist:
            return Response('bad request3')
        
        try:
            user = User.objects.get(pk = student_id)
        except User.DoesNotExist:
            return Response('bad request3')

        if contest_id not in contests:
            contest_rooms = ContestRooms()
            contests[contest_id] = contest_rooms
        else:
            contest_rooms = contests[contest_id]

        rooms_queue = contest_rooms.wait_rooms
        if rooms_queue.empty:
            room = self.create_room(student_id, contest)
        else:
            room = self.choose_room(student_id, contest, contest_rooms)
        return Response({"channelId": f"{room.channel_id}"})

    def create_room(self, user_id, contest):
        room_queue = contests[contest.contest_id]
        room = Room(user_id, contest.participant_number)
        rooms[room.channel_id] = room
        room.add_user(user_id)
        room_queue.put(room)
        return room

    def choose_room(self, user_id, contest, contest_rooms):
        room_queue = contests[contest.contest_id]
        while (room_queue.empty == False):
            room = room_queue.queue[0]
            if room.bis_empty:
                room_queue.get()
                continue
            else: 
                room.add_user(user_id)
                if room.bis_full:
                    room_queue.get()
                    room.set_status(RoomStatus.READY)
                    self.room_ready(room, contest_rooms)
                return room
        else:
            return self.create_room(room_queue, user_id, contest)

    def room_ready(self, room, contest_rooms):
        channel_id = room.channel_id
        time.sleep(1)
        url = ""
        payload = {
            "type": 1, 
            "content": "request ready!"
            }
        requests.post(url, data=payload)
        timer = Timer(10.0, self.room_check_ready, (room, contest_rooms))


    def room_check_ready(self, room, contest_rooms):
        if room.bis_all_ready:
            return
        else:
          self.room_clear(room, contest_rooms)  

    def room_clear(self, room, contest_rooms):
        sz = room.total_count
        ready_list = room.ready_list
        del_cnt = 0
        for i in range(sz):
            if ready_list[i] == False:
                room.delete_user_index(i - del_cnt)
                del_cnt += 1
        room.clear_ready()
        contest_rooms.wait_rooms.put(room)
        url = ""
        payload = {
            "type": 2, 
            "content": "room clear!"
            }
        requests.post(url, data=payload)


class CancelView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        data = request.data
        if 'studentId' in data:
            student_id = data['studentId']
        else:
            return Response('bad request1')

        if 'channelId' in data:
            channel_id = data['channelId']
        else:
            return Response('bad request2')
        
        try:
            user = User.objects.get(pk = student_id)
        except User.DoesNotExist:
            return Response('bad request3')

        if channel_id in rooms:
            room = rooms[channel_id]
        else:  
            return Response('bad request3')

        room.delete_user(user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

