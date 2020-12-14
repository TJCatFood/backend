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
from course.models import Teach


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
            return Response(content)
        except:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content)

    def post(self, request, course_id):
        if request.user.character == 4:
            # FIXME: 4->1
            weight = GradeProportion(course_id=course_id, assignment=1, exam1=1, exam2=1, experiment=1, contest=1,
                                     attendance=1)
            weight.save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': f"grade weight of {course_id} created successfully"
                }
            }
            return Response(content)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you are not the charging teacher"
                }
            }
            return Response(content)

    def put(self, request, course_id):
        print(request.user.character)
        if request.user.character == 4 or request.user.character == 2:
            # FIXME: 4->1
            # TODO: judge whether the teacher is teaching this course
            if request.user.character == 4:
                # FIXME: just for easier test, should do the judgement above
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
                    return Response(content, status=400)
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
                return Response(content)
            except:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "no such course"
                    }
                }
                return Response(content)

        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content)


class GradeView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeachingAssistant | IsTeacher | IsChargingTeacher]

    def get(self, request, course_id, student_id):
        # TODO: judge whether the teacher is teaching this course

        if request.user.user_id == student_id or request.user.character == 1:
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
                return Response(content)
            else:
                content = {
                    'isSuccess': False,
                    'data': {
                        'message': "no such course or student hasn't took the course or the grade hasn't been released"
                    }
                }
                return Response(content)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "you don't have the competence"
                }
            }
            return Response(content)


class GradesView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeacher | IsChargingTeacher]

    # FIXME: delete the student above

    def get(self, request, course_id):
        # TODO: judge whether the teacher is teaching this course
        grades = Grade.objects.filter(course_id=course_id)
        if grades:
            all_grades = []
            for grade in grades:
                one_content = {
                    'student_id': f"{grade.student_id}",
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
            return Response(content)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course or the grade hasn't been released"
                }
            }
            return Response(content)

    def post(self, request, course_id):
        # TODO: judge whether the teacher is teaching this course
        take_courses = TakeCourse.objects.filter(course_id=course_id)
        if take_courses:
            for take_course in take_courses:
                student_id = take_course.student_id
                try:
                    # TODO: get all the grades
                    assignment_point = 90
                    exam1_point = 90
                    exam2_point = 90
                    experiment_point = 90
                    contest_point = 90
                    attendance_point = 90
                    bonus_point = 0
                except:
                    assignment_point = 0
                    exam1_point = 0
                    exam2_point = 0
                    experiment_point = 0
                    contest_point = 0
                    attendance_point = 0
                    bonus_point = 0
                try:
                    weight = GradeProportion.objects.get(course_id=course_id)
                    assignment = weight.assignment
                    exam1 = weight.exam1
                    exam2 = weight.exam2
                    experiment = weight.experiment
                    contest = weight.contest
                    attendance = weight.attendance
                except:
                    content = {
                        'isSuccess': False,
                        'data': {
                            'message': "no weight set"
                        }
                    }
                total_weight = assignment + exam1 + exam2 + experiment + content + attendance
                total_point = assignment_point * (assignment / total_weight) + exam1_point * (
                        exam1 / total_weight) + exam2_point * (exam2 / total_weight) + experiment_point * (
                                      experiment / total_weight) + contest_point * (
                                      contest / total_weight) + attendance_point * (
                                      attendance / total_weight) + bonus_point
                grade = Grade(course_id=course_id, student_id=student_id, assignment_point=assignment_point,
                              exam1_point=exam1_point, exam2_point=exam2_point, experiment_point=experiment_point,
                              contest_point=contest_point, attendance_point=attendance_point, bonus_point=bonus_point,
                              total_point=total_point)
                grade.save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': f"grades of course {course_id} have been released"
                }
            }
            return Response(content)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content)

    def put(self, request, course_id):
        # TODO: judge whether the teacher is teaching this course
        grades = Grade.objects.filter(course_id=course_id)
        if grades:
            for grade in grades:
                student_id = grade.student_id
                try:
                    # TODO: get all the grades
                    assignment_point = 90
                    exam1_point = 90
                    exam2_point = 90
                    experiment_point = 90
                    contest_point = 90
                    attendance_point = 90
                    bonus_point = 0
                except:
                    assignment_point = 0
                    exam1_point = 0
                    exam2_point = 0
                    experiment_point = 0
                    contest_point = 0
                    attendance_point = 0
                    bonus_point = 0
                try:
                    weight = GradeProportion.objects.get(course_id=course_id)
                    assignment = weight.assignment
                    exam1 = weight.exam1
                    exam2 = weight.exam2
                    experiment = weight.experiment
                    contest = weight.contest
                    attendance = weight.attendance
                except:
                    content = {
                        'isSuccess': False,
                        'data': {
                            'message': "no weight set"
                        }
                    }
                total_weight = assignment + exam1 + exam2 + experiment + content + attendance
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
                grade.bonus_point = bonus_point
                grade.total_point = total_point
                grade.save()
            content = {
                'isSuccess': True,
                'data': {
                    'message': f"grades of course {course_id} have been updated"
                }
            }
            return Response(content)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "no such course"
                }
            }
            return Response(content)


class BonusView(APIView):
    authentication_classes = [CatfoodAuthentication]
    permission_classes = [IsStudent | IsTeacher | IsChargingTeacher]

    # FIXME: delete the student above

    def post(self, request, course_id, student_id):
        # TODO: judge whether the teacher is teaching this course
        try:
            bonus_point = request.data["bonus_point"]
        except:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "bonus point needed"
                }
            }
            return Response(content)
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
            return Response(content)
        else:
            content = {
                'isSuccess': False,
                'data': {
                    'message': "please release the grades first"
                }
            }
            return Response(content)
