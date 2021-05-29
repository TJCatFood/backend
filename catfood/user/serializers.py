from rest_framework import serializers
from .models import University, School, TakeCourse


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = [
            'university_id',
            'official_id',
            'university_name',
        ]


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'school_id',
            'school_name',
            'university_id',
        ]


class TakeCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TakeCourse
        fields = [
            'student_id',
            'course_id',
            'active',
        ]
