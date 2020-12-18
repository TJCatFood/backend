from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from user.authentication import CatfoodAuthentication
from user.permissions import IsStudent, IsTeachingAssistant, IsTeacher, IsChargingTeacher
from rest_framework import status
from django.utils.datastructures import MultiValueDictKeyError
from .models import Grade, GradeProportion
from user.models import TakeCourse
from .serializers import GradeProportionSerializer, GradeSerializer
from course.models import Teach, Course


def get_experiment(course_id, student_id):
    return 90


def get_contest(course_id, student_id):
    return 90


def get_assignment(course_id, student_id):
    return 90


def get_exam1(course_id, student_id):
    return 90


def get_exam2(course_id, student_id):
    return 90


def get_attendance(course_id, student_id):
    return 100


# Create your views here.

class GradeWeightView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id):
        try:
            weight = GradeProportion.objects.get(course_id=course_id)
            assignment = weight.assignment
            exam1 = weight.exam1
            exam2 = weight.exam2
            experiment = weight.experiment
            contest = weight.contest
            attendance = weight.attendance
            content = {
                'isSuccess': True,
                'data': {
                    'assignment': f"{assignment}",
                    'exam1': f"{exam1}",
                    'exam2': f"{exam2}",
                    'experiment': f"{experiment}",
                    'contest': f"{contest}",
                    'attendance': f"{attendance}",
                }
            }
            return Response(content, status=status.HTTP_200_OK)
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id):
        # should be done when the course is created
        if request.user.character == 1:
            course = Course.objects.get(course_id=course_id)
            weight = GradeProportion(course_id=course, assignment=1, exam1=1, exam2=1, experiment=1, contest=1,
                                     attendance=1)
            weight.save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': f"grade weight of {course_id} created successfully"
                }
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you are not the charging teacher"
                }
            }
            return Response(content, status=status.HTTP_200_OK)

    def put(self, request, course_id):
        try:
            teach = Teach.objects.get(course_id=course_id)
            if teach.teacher_id.user_id == request.user.user_id and request.user.character != 3:
                pass
            else:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "you don't teach this course"
                    }
                }
                return Response(content, status=status.HTTP_200_OK)
        except Exception:
            print(114514)
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content, status=status.HTTP_200_OK)
        try:
            assignment = request.data['assignment']
            exam1 = request.data['exam1']
            exam2 = request.data['exam2']
            experiment = request.data['experiment']
            contest = request.data['contest']
            attendance = request.data['attendance']
        except MultiValueDictKeyError:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "缺少必填信息"
                }
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            weight = GradeProportion.objects.get(course_id=course_id)
            weight.assignment = assignment
            weight.exam1 = exam1
            weight.exam2 = exam2
            weight.experiment = experiment
            weight.contest = contest
            weight.attendance = attendance
            weight.save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': "updated successfully"
                }
            }
            return Response(content, status=status.HTTP_201_CREATED)
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)


class GradeView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, student_id):
        try:
            course = Course.objects.get(course_id=course_id)
            if not course.course_is_score_public:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "the grade hasn't been released"
                    }
                }
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        if request.user.user_id == student_id:
            search_dict = dict()
            search_dict['course_id'] = course_id
            search_dict['student_id'] = student_id
            grade = Grade.objects.filter(**search_dict)
            if grade:
                content = {
                    'isSuccess': True,
                    'data': {
                        'assignment_point': f"{grade[0].assignment_point}",
                        'exam1_point': f"{grade[0].exam1_point}",
                        'exam2_point': f"{grade[0].exam2_point}",
                        'experiment_point': f"{grade[0].experiment_point}",
                        'contest_point': f"{grade[0].contest_point}",
                        'attendance_point': f"{grade[0].attendance_point}",
                        'bonus_point': f"{grade[0].bonus_point}",
                        'total_point': f"{grade[0].total_point}",
                    }
                }
                return Response(content, status=status.HTTP_200_OK)
            else:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "no such course or student hasn't took the course or the grade hasn't been released"
                    }
                }
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content, status=status.HTTP_200_OK)


class GradesView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsTeacher | IsChargingTeacher]

    def get(self, request, course_id):
        # judge whether the teacher is teaching this course
        try:
            teach = Teach.objects.get(course_id=course_id)
            if teach.teacher_id.user_id == request.user.user_id and request.user.character != 3:
                pass
            else:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "you don't have the competence"
                    }
                }
                return Response(content, status=status.HTTP_200_OK)
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content, status=status.HTTP_200_OK)
        grades = Grade.objects.filter(course_id=course_id)
        if grades:
            all_grades = []
            for grade in grades:
                one_content = {
                    'student_id': f"{grade.student_id.user_id}",
                    'assignment_point': f"{grade.assignment_point}",
                    'exam1_point': f"{grade.exam1_point}",
                    'exam2_point': f"{grade.exam2_point}",
                    'experiment_point': f"{grade.experiment_point}",
                    'contest_point': f"{grade.contest_point}",
                    'attendance_point': f"{grade.attendance_point}",
                    'bonus_point': f"{grade.bonus_point}",
                    'total_point': f"{grade.total_point}",
                }
                all_grades.append(one_content)
            content = {
                'isSuccess': True,
                'data': all_grades
            }
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course or the grade hasn't been released"
                }
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id):
        # judge whether the teacher is teaching this course
        try:
            teach = Teach.objects.get(course_id=course_id)
            if teach.teacher_id.user_id == request.user.user_id and request.user.character != 3:
                pass
            else:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "you don't have the competence"
                    }
                }
                return Response(content, status=status.HTTP_200_OK)
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content, status=status.HTTP_200_OK)
        take_courses = TakeCourse.objects.filter(course_id=course_id)
        if take_courses:
            course = Course.objects.get(course_id=course_id)
            for take_course in take_courses:
                student_id = take_course.student_id
                grade = Grade(course_id=course, student_id=student_id, assignment_point=0,
                              exam1_point=0, exam2_point=0, experiment_point=0,
                              contest_point=0, attendance_point=0, bonus_point=0,
                              total_point=0)
                grade.save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': f"grades of course {course_id} have been released"
                }
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, course_id):
        # judge whether the teacher is teaching this course
        try:
            teach = Teach.objects.get(course_id=course_id)
            if teach.teacher_id.user_id == request.user.user_id and request.user.character != 3:
                pass
            else:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "you don't have the competence"
                    }
                }
                return Response(content, status=status.HTTP_200_OK)
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content, status=status.HTTP_200_OK)
        grades = Grade.objects.filter(course_id=course_id)
        if grades:
            try:
                weight = GradeProportion.objects.get(course_id=course_id)
                assignment = weight.assignment
                exam1 = weight.exam1
                exam2 = weight.exam2
                experiment = weight.experiment
                contest = weight.contest
                attendance = weight.attendance
            except Exception:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "no weight set"
                    }
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            for grade in grades:
                student_id = grade.student_id
                try:
                    # TODO: get all the grades
                    assignment_point = get_assignment(course_id, student_id)
                    exam1_point = get_exam1(course_id, student_id)
                    exam2_point = get_exam2(course_id, student_id)
                    experiment_point = get_experiment(course_id, student_id)
                    contest_point = get_contest(course_id, student_id)
                    attendance_point = get_attendance(course_id, student_id)
                except Exception:
                    assignment_point = 0
                    exam1_point = 0
                    exam2_point = 0
                    experiment_point = 0
                    contest_point = 0
                    attendance_point = 0
                bonus_point = grade.bonus_point
                total_weight = assignment + exam1 + exam2 + experiment + contest + attendance
                total_point = assignment_point * (assignment / total_weight) + exam1_point * (
                        exam1 / total_weight) + exam2_point * (exam2 / total_weight) + experiment_point * (
                                      experiment / total_weight) + contest_point * (
                                      contest / total_weight) + attendance_point * (
                                      attendance / total_weight) + bonus_point
                grade.assignment_point = assignment_point
                grade.exam1_point = exam1_point
                grade.exam2_point = exam2_point
                grade.experiment_point = experiment_point
                grade.contest_point = contest_point
                grade.attendance_point = attendance_point
                grade.total_point = total_point
                grade.save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': f"grades of course {course_id} have been updated"
                }
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)


class BonusView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsTeacher | IsChargingTeacher]

    def post(self, request, course_id, student_id):
        # judge whether the teacher is teaching this course
        try:
            teach = Teach.objects.get(course_id=course_id)
            if teach.teacher_id.user_id == request.user.user_id and request.user.character != 3:
                pass
            else:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "you don't have the competence"
                    }
                }
                return Response(content, status=status.HTTP_200_OK)
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content, status=status.HTTP_200_OK)
        try:
            bonus_point = request.data["bonus_point"]
        except Exception:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "bonus point needed"
                }
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        search_dict = dict()
        search_dict['course_id'] = course_id
        search_dict['student_id'] = student_id
        grade = Grade.objects.filter(**search_dict)
        if grade:
            grade[0].bonus_point = bonus_point
            grade[0].save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': "bonus set successfully"
                }
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no grade found"
                }
            }
            return Response(content, status=status.HTTP_200_OK)
