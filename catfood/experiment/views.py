from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from course_database.models import ExperimentCaseDatabase
from experiment.models import CourseCase, ExperimentAssignment
from experiment.serializers import ExperimentCaseDatabaseSerializer, CourseCaseSerializer, ExperimentAssignmentSerializer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from experiment import utils
from course.models import Course, Teach


class TestView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        response = 'test succeed!'
        content = {
            "response": f"{response}"
        }
        return Response(content)


@api_view(['GET', 'POST'])
@permission_classes([IsChargingTeacher | IsTeacher])
@authentication_classes([CatfoodAuthentication])
def experiment_case_list(request):
    """
    List all cases, or create a new case.
    """
    if request.method == 'GET':
        cases = ExperimentCaseDatabase.objects.all()
        serializer = ExperimentCaseDatabaseSerializer(cases, many=True)
        return Response(utils.generate_response(serializer.data, True))
    elif request.method == 'POST':
        serializer = ExperimentCaseDatabaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        else:
            return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsChargingTeacher | IsTeacher])
@authentication_classes([CatfoodAuthentication])
def experiment_case_detail(request, pk):
    """
    Retrieve, update or delete a experiment case instance.
    """
    try:
        case = ExperimentCaseDatabase.objects.get(pk=pk)
    except ExperimentCaseDatabase.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentCaseDatabaseSerializer(case)
        return Response(utils.generate_response(serializer.data, True))

    elif request.method == 'PUT':
        serializer = ExperimentCaseDatabaseSerializer(
            case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True))
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def course_case_list(request, course_id):
    """
    List all cases of a specific course, or bind a case to this course.
    """
    if request.method == 'GET':
        cases = CourseCase.objects.all()
        cases = cases.filter(course_id=course_id)
        serializer = CourseCaseSerializer(cases, many=True)
        for index, case in enumerate(serializer.data):
            case_id = case['case_id']
            case_info = ExperimentCaseDatabase.objects.get(experiment_case_id=case_id)
            case_ser = ExperimentCaseDatabaseSerializer(case_info)
            serializer.data[index]['experiment_name'] = case_ser.data['experiment_name']
            serializer.data[index]['experiment_case_description'] = case_ser.data['experiment_case_description']
        return Response(utils.generate_response(serializer.data, True))

    elif request.method == 'POST':
        #  只有责任老师和老师才有创建的权限
        if request.user.character not in [1, 2]:
            error_msg = {"detail": "没有权限"}
            return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        elif request.user.character in [2]:
            try:
                print('*'*10, course_id, request.user.user_id, '*'*10)
                teach = Teach.objects.get(course_id=course_id, teacher_id=request.user.user_id)
            except Teach.DoesNotExist:
                error_msg = {"detail": "没有权限"}
                return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = CourseCaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def course_case_detail(request, pk):
    """
    Retrieve, update or delete a course case instance.
    """
    try:
        case = CourseCase.objects.get(pk=pk)
    except CourseCase.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CourseCaseSerializer(case)
        return Response(utils.generate_response(serializer.data, True))

    elif request.method == 'PUT':
        if request.user.character not in [1, 2]:
            error_msg = {"detail": "没有权限"}
            return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        elif request.user.character in [2]:
            try:
                print('*'*10, course_id, request.user.user_id, '*'*10)
                teach = Teach.objects.get(course_id=course_id, teacher_id=request.user.user_id)
            except Teach.DoesNotExist:
                error_msg = {"detail": "没有权限"}
                return Response(utils.generate_response(error_msg, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = CourseCaseSerializer(
            case, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True))
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsStudent])
@authentication_classes([CatfoodAuthentication])
def assignment_student_list(request):
    """
    List all assignments for a particular student.
    Submit a assignment
    """
    if request.method == 'GET':
        assignments = ExperimentAssignment.objects.filter(submission_uploader=request.user.user_id)
        # TODO: 获取学生信息，用于过滤
        # assignments = assignments.filter()
        serializer = ExperimentAssignmentSerializer(assignments, many=True)
        return Response(utils.generate_response(utils.student_assignments_filter(serializer.data), True))

    elif request.method == 'POST':
        # TODO: 鉴权
        serializer = ExperimentAssignmentSerializer(data=request.data)
        if not utils.is_submission_valid(request.data):
            return Response(utils.generate_response({"error_msg": 'permission denied'}, False), status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True), status=status.HTTP_201_CREATED)
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)


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
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentAssignmentSerializer(assignment)
        return Response(utils.generate_response(utils.student_assignments_filter([serializer.data])[0], True))

    elif request.method == 'PUT':
        old_assignment = ExperimentAssignmentSerializer(assignment).data
        if not utils.is_submission_retrieve_valid(old_assignment, request.data):
            return Response(utils.generate_response({"error_msg": 'permission denied'}, False), status=status.HTTP_400_BAD_REQUEST)
        serializer = ExperimentAssignmentSerializer(
            assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True))
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not utils.is_submission_delete_valid(
                ExperimentAssignmentSerializer(assignment).data):
            response_data = {"error_msg": 'permission denied'}
            return Response(utils.generate_response(response_data, False), status=status.HTTP_400_BAD_REQUEST)
        assignment.delete()
        response_data = {"detail": "have delete"}
        return Response(utils.generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)


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
        return Response(utils.generate_response(serializer.data, True))


@api_view(['GET', 'PUT', 'DELETE'])
def assignment_teacher_detail(request, pk):
    """
    Retrieve, update or delete a assignment submission instance.
    """
    try:
        assignment = ExperimentAssignment.objects.get(pk=pk)
    except ExperimentAssignment.DoesNotExist:
        error_data = {"detail": "not exist"}
        return Response(utils.generate_response(error_data, False), status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentAssignmentSerializer(assignment)
        return Response(utils.generate_response(serializer.data, True))

    elif request.method == 'PUT':
        serializer = ExperimentAssignmentSerializer(
            assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(utils.generate_response(serializer.data, True))
        return Response(utils.generate_response(serializer.errors, False), status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        assignment.delete()
        response_data = {"detail": "have delete"}
        return Response(utils.generate_response(response_data, True), status=status.HTTP_204_NO_CONTENT)
