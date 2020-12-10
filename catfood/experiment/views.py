from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from course_database.models import ExperimentCaseDatabase
from experiment.models import CourseCase, ExperimentAssignment
from experiment.serializers import ExperimentCaseDatabaseSerializer, CourseCaseSerializer, ExperimentAssignmentSerializer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from experiment.utils import generate_response, dict_filter, student_assignments_filter, is_submission_valid, is_submission_retrieve_valid, is_submission_delete_valid 

class TestView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, format=None):
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response(content)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def experiment_case_list(request):
    """
    List all cases, or create a new case.
    TODO: 必须有教师或责任教师权限
    """
    if request.method == 'GET':
        # TODO: 分页
        cases = ExperimentCaseDatabase.objects.all()
        serializer = ExperimentCaseDatabaseSerializer(cases, many=True) 
        return Response(generate_response(serializer.data, True))
    elif request.method == 'POST':
        serializer = ExperimentCaseDatabaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        else:
            return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def experiment_case_detail(request, pk):
    """
    Retrieve, update or delete a experiment case instance.
    TODO: 必须有教师或者责任教师的权限
    """
    try:
        case = ExperimentCaseDatabase.objects.get(pk=pk)
    except ExperimentCaseDatabase.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(generate_response(error_data, False),status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentCaseDatabaseSerializer(case)
        return Response(generate_response(serializer.data, True))

    elif request.method == 'PUT':
        serializer = ExperimentCaseDatabaseSerializer(
            case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True))
        return Response(generate_response(cserializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        case.delete()
        response_data = {"detail": "have delete"}
        return Response(generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_case_list(request, course_id):
    """
    List all cases of a specific course, or bind a case to this course.
    """
    # TODO: 鉴权
    if request.method == 'GET':
        cases = CourseCase.objects.all()
        cases = cases.filter(course_id=course_id)
        serializer = CourseCaseSerializer(cases, many=True)
        return Response(generate_response(serializer.data, True))

    elif request.method == 'POST':
        serializer = CourseCaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def course_case_detail(request, pk):
    """
    Retrieve, update or delete a course case instance.
    TODO: 必须有责任教师的权限
    """
    try:
        case = CourseCase.objects.get(pk=pk)
    except CourseCase.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(generate_response(error_data, False),status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CourseCaseSerializer(case)
        return Response(generate_response(serializer.data, True))

    elif request.method == 'PUT':
        serializer = CourseCaseSerializer(
            case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True))
        return Response(generate_response(cserializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        case.delete()
        response_data = {"detail": "have delete"}
        return Response(generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def assignment_student_list(request):
    """
    List all assignments for a particular student.
    Submit a assignment
    """
    if request.method == 'GET':
        assignments = ExperimentAssignment.objects.all()
        # TODO: 鉴权
        # TODO: 获取学生信息，用于过滤
        # assignments = assignments.filter()
        serializer = ExperimentAssignmentSerializer(assignments, many=True)
        return Response(generate_response(student_assignments_filter(serializer.data)), True)

    elif request.method == 'POST':
        # TODO: 鉴权
        serializer = ExperimentAssignmentSerializer(data=request.data)
        if not is_submission_valid(request.data):
            return Response(generate_response({"error_msg": 'permission denied'}, False), status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def assignment_student_detail(request, pk):
    """
    Retrieve, update or delete a assignment submission instance.
    """
    try:
        assignment = ExperimentAssignment.objects.get(pk=pk)
    except ExperimentAssignment.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(generate_response(error_data, False),status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        serializer = ExperimentAssignmentSerializer(assignment)
        return Response(generate_response(student_assignments_filter([serializer.data])[0]), True)

    elif request.method == 'PUT':
        old_assignment = ExperimentAssignmentSerializer(assignment).data
        if not is_submission_retrieve_valid(old_assignment, request.data):
            return Response(generate_response({"error_msg": 'permission denied'}, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = ExperimentAssignmentSerializer(
            assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data), True)
        return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not is_submission_delete_valid(
                ExperimentAssignmentSerializer(assignment).data):
            response_data = {"error_msg": 'permission denied'}
            return Response(generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)
        assignment.delete()
        response_data = {"detail": "have delete"}
        return Response(generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def assignment_teacher_list(request, course_case_id):
    """
    List all the assignments with a specific course_case_id for teacher.
    """
    if request.method == 'GET':
        assignments = ExperimentAssignment.objects.all()
        # TODO: 鉴权
        assignments = assignments.filter(course_case_id=course_case_id)
        serializer = ExperimentAssignmentSerializer(assignments, many=True)
        return Response(generate_response(serializer.data), True)


@api_view(['GET', 'PUT', 'DELETE'])
def assignment_teacher_detail(request, pk):
    """
    Retrieve, update or delete a assignment submission instance.
    """
    try:
        assignment = ExperimentAssignment.objects.get(pk=pk)
    except ExperimentAssignment.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(generate_response(error_data, False),status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentAssignmentSerializer(assignment)
        return Response(generate_response(serializer.data), True)

    elif request.method == 'PUT':
        serializer = ExperimentAssignmentSerializer(
            assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(generate_response(serializer.data), True)
        return Response(generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        assignment.delete()
        response_data = {"detail": "have delete"}
        return Response(generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)




