from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from experiment.models import CourseCase, ExperimentAssignment
from experiment.serializers import CourseCaseSerializer, ExperimentAssignmentSerializer
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher

from experiment import utils
from user.models import TakeCourse
from user.serializers import TakeCourseSerializer


@api_view(['GET'])
@permission_classes([IsChargingTeacher | IsTeacher | IsTeachingAssistant | IsStudent])
@authentication_classes([CatfoodAuthentication])
def get_course_case_statistics(request, course_case_id):
    course_case = CourseCase.objects.get(course_case_id=course_case_id)
    course_id = CourseCaseSerializer(course_case).data['course_id']
    print(course_id)
    takes = TakeCourseSerializer(TakeCourse.objects.all().filter(course_id=course_id), many=True).data
    # 选课人数
    user_id_list = [take['student_id'] for take in takes]
    print(user_id_list)
    # 提交人数
    assignment_list = ExperimentAssignmentSerializer(ExperimentAssignment.objects.all().filter(course_case_id=course_case_id), many=True).data
    submission_num = len(assignment_list)
    print(submission_num)
    # 已批改的人数
    remarked_list = [assignment for assignment in assignment_list if assignment['submission_score'] > 0]
    remarked_num = len(remarked_list)
    # 分数段 0-60 61-70 71-80 81-90 91-100
    score_distributed = [0, 0, 0, 0, 0]
    for remarked in remarked_list:
        if remarked['submission_score'] <= 60:
            score_distributed[0] += 1
        elif remarked['submission_score'] <= 70:
            score_distributed[1] += 1
        elif remarked['submission_score'] <= 80:
            score_distributed[2] += 1
        elif remarked['submission_score'] <= 90:
            score_distributed[3] += 1
        elif remarked['submission_score'] <= 100:
            score_distributed[4] += 1
    answer = {
        'submitted_num': submission_num,
        'unsubmitted_num': len(user_id_list) - submission_num,
        'remarked_num': remarked_num,
        'unremarked_num': submission_num - remarked_num,
        'score_distributed': score_distributed,
    }
    return Response(utils.generate_response(answer, True))
