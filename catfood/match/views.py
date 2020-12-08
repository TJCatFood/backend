from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
              
from match import room


rooms = {}
contests = {}


class TestView(APIView):

    def get(self, request, format=None):
        room1 = room.Room(None, 3)
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response(content)
