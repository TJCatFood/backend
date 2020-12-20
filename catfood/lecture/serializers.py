from rest_framework import serializers
from .models import *


class CourseChapterDescrptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseChapterDescrption
        fields = [
            'course_chapter_description_id',
            'course_id',
            'course_chapter_id',
            'course_chapter_title',
            'course_chapter_mooc_link',
        ]


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = [
            'homework_id',
            'course_id',
            'homework_creator',
            'homework_description',
            'homework_start_timestamp',
            'homework_end_timestamp',
        ]


class HomeworkScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkScore
        fields = [
            'homework_id',
            'student_id',
            'homework_student_grade',
            'homework_teachers_comments',
            'homework_is_grade_available_to_students',
        ]


class HomeworkFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkFile
        fields = [
            'file_homework_id',
            'homework_id',
            'file_uploader',
            'file_timestamp',
            'file_token',
        ]
