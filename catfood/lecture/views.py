from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view


class AliveView(APIView):

    def get(self, request, format=None):
        response = 'alive'
        content = {
            "response": f"{response}"
        }
        return Response(content)
