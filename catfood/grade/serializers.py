from rest_framework import serializers
from .models import Grade, GradeProportion


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = [
            'course_id',
            'student_id',
            'assignment_point',
            'exam1_point',
            'exam2_point',
            'experiment_point',
            'contest_point',
            'attendance_point',
            'bonus_point',
            'total_point',
        ]


class GradeProportionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeProportion
        fields = [
            'course_id',
            'assignment',
            'exam1',
            'exam2',
            'experiment',
            'contest',
            'attendance',
        ]
