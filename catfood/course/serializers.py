from rest_framework import serializers
from course.models import Course, Teach
from experiment.models import CourseCase


class CourseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'course_id',
            'course_creator_school_id',
            'course_name',
            'course_description',
            'course_credit',
            'course_study_time_needed',
            'course_type',
            'course_start_time',
            'course_end_time',
            'course_avatar',
            'course_is_score_public',
        ]


class TeachSerializers(serializers.ModelSerializer):
    class Meta:
        model = Teach
        fields = [
            'course_id',
            'teacher_id',
            'course_teach_id',
        ]
