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
    # permission_classes = (AllowAny,)
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
        serializer = ExperimentCaseDatabaseSerializer(
            case, data=request.data, partial=True)
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
        return Response(student_assignments_filter(serializer.data))

    elif request.method == 'POST':
        # TODO: 鉴权
        serializer = ExperimentAssignmentSerializer(data=request.data)
        if not is_submission_valid(request.data):
            return Response({"error_msg": 'permission denied'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def assignment_student_detail(request, pk):
    """
    Retrieve, update or delete a assignment submission instance.
    """
    try:
        assignment = ExperimentAssignment.objects.get(pk=pk)
    except ExperimentAssignment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentAssignmentSerializer(assignment)
        return Response(student_assignments_filter([serializer.data])[0])

    elif request.method == 'PUT':
        old_assignment = ExperimentAssignmentSerializer(assignment).data
        if not is_submission_retrieve_valid(old_assignment, request.data):
            return Response({"error_msg": 'permission denied'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ExperimentAssignmentSerializer(
            assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not is_submission_delete_valid(
                ExperimentAssignmentSerializer(assignment).data):
            return Response({"error_msg": 'permission denied'}, status=status.HTTP_400_BAD_REQUEST)
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def assignment_teacher_list(request, course_case_id):
    """
    List all the assignments with a specific course_case_id for teacher.
    """
    if request.method == 'GET':
        assignments = ExperimentAssignment.objects.all()
        # TODO: 鉴权
        assignments = assignments.filter(course_case_id=course_case_id)
        serializer = ExperimentAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def assignment_teacher_detail(request, pk):
    """
    Retrieve, update or delete a assignment submission instance.
    """
    try:
        assignment = ExperimentAssignment.objects.get(pk=pk)
    except ExperimentAssignment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperimentAssignmentSerializer(assignment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ExperimentAssignmentSerializer(
            assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def dict_filter(old_dict, keys):
    ans = {}
    for key in keys:
        ans[key] = old_dict[key]
    return ans


def student_assignments_filter(assignments_list):
    key_white_list = ['course_case_id',
                      'submission_uploader', 'submission_file_token', 'submission_case_id']
    for index, assignment in enumerate(assignments_list):
        if not assignment['submission_is_public']:
            assignments_list[index] = dict_filter(assignment, key_white_list)
    return assignments_list


def is_submission_valid(submission):
    key_white_list = ['course_case_id',
                      'submission_uploader', 'submission_file_token']
    for key in submission.keys():
        if key not in key_white_list:
            return False
    return True


def is_submission_retrieve_valid(old_submission, new_submission):
    if old_submission['submission_is_public']:
        return False
    key_white_list = ['course_case_id',
                      'submission_uploader', 'submission_file_token', 'submission_case_id']
    for key in new_submission.keys():
        if key not in key_white_list:
            return False
    return True


def is_submission_delete_valid(old_submission):
    if old_submission['submission_is_public']:
        return False
    return True
