from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view
from course_database.models import ExperimentCaseDatabase
from experiment.models import CourseCase, ExperimentAssignment
from experiment.serializers import ExperimentCaseDatabaseSerializer, CourseCaseSerializer, ExperimentAssignmentSerializer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from rest_framework import generics

class TestView(APIView):

    def get(self, request, format=None):
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response(content)


@api_view(['GET', 'POST'])
def experiment_case_list(request):
    """
    List all cases, or create a new case.
    """
    # TODO: 鉴权
    if request.method == 'GET':
        # TODO: 分页
        cases = ExperimentCaseDatabase.objects.all()
        serializer = ExperimentCaseDatabaseSerializer(cases, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExperimentCaseDatabaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def experiment_case_detail(request, pk):
    """
    Retrieve, update or delete a experiment case instance.
    """
    try:
        case = ExperimentCaseDatabase.objects.get(pk=pk)
    except ExperimentCaseDatabase.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentCaseDatabaseSerializer(case)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ExperimentCaseDatabaseSerializer(case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        case.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def course_case_list(request, course_id):
    """
    List all cases of a specific course, or bind a case to this course.
    """
    # TODO: 鉴权
    if request.method == 'GET':
        cases = CourseCase.objects.all()
        cases = cases.filter(course_id=course_id)
        serializer = CourseCaseSerializer(cases, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CourseCaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseCasesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseCase.objects.all()
    serializer_class = CourseCaseSerializer

@api_view(['GET', 'POST'])
def assignment_list(request, course_case_id):
    """
    List all cases of a specific assignments.
    """
    if request.method == 'GET':
        assignments = ExperimentAssignment.objects.all()
        assignments = assignments.filter(course_case_id=course_case_id)
        serializer = ExperimentAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExperimentAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)