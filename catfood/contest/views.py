from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['GET'])
def get_matches(request):
    params = request.query_params
    content = {
        "params": f"{params}",
        "response": 'get_matches test succeed'
    }
    return Response(content)


@api_view(['GET'])
def get_match(request, match_id):
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


class TestView(APIView):

    def get(self, request, format=None):
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response(content)


class ContestView(APIView):

    def get(self, request, format=None):
        return Response('get_contest test succeed')

    def post(self, request, format=None):
        data = request.data
        return Response(data, status=status.HTTP_201_CREATED)


class MatchesVIew(APIView):

    def get(self, request, contest_id, format=None):
        params = request.query_params.dict()
        response_type = params['type']
        if response_type == '0':
            return self.get_contest_matches(contest_id)
        elif response_type == '1':
            return self.get_student_matches(contest_id)
        else:
            return Response('Bad Request!', status=status.HTTP_400_BAD_REQUEST)

    def get_contest_matches(self, contest_id):
        content = {
            "contest_id": f"{contest_id}",
            "response": 'get_contest_matches test succeed'
        }
        return Response(content)

    def get_student_matches(self, contest_id):
        content = {
            "contest_id": f"{contest_id}",
            "response": 'get_student_matches test succeed'
        }
        return Response(content)
