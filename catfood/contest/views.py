from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

from contest.serializer import ContestSerializer
from contest import models


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


@api_view(['GET'])
def get_matches_student(request):
    params = request.query_params
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


@api_view(['GET'])
def get_matchid(request):
    params = request.query_params
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


@api_view(['GET'])
def get_contest_questions(request, contest_id):
    params = request.query_params
    content = {
        "matchId": f"{match_id}",
        "response": 'get_match test succeed'
    }
    return Response(content)


@api_view(['GET'])
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
        response_type = params['type']
        if response_type == '0':
            return self.get_contest_matches(contest_id)
        elif response_type == '1':
            return self.get_student_matches(contest_id)
        else:
            return Response('Bad Request!', status=status.HTTP_400_BAD_REQUEST)

    def get_contest_matches(self, contest_id):
        content = {
            "contestId": f"{contest_id}",
            "response": 'get_contest_matches test succeed'
        }
        return Response(content)

    def get_student_matches(self, contest_id):
        content = {
            "contestId": f"{contest_id}",
            "response": 'get_student_matches test succeed'
        }
        return Response(content)
