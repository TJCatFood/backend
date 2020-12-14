from rest_framework import serializers
from .models import CourseDocument, ExperimentDocument


class CourseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDocument
        fields = [
            'file_course_document_id',
            'course_id',
            'file_display_name',
            'file_comment',
            'file_create_timestamp',
            'file_update_timestamp',
            'file_uploader',
            'file_token',
        ]


class ExperimentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentDocument
        fields = [
            'file_experiment_document_id',
            'course_id',
            'file_display_name',
            'file_comment',
            'file_create_timestamp',
            'file_update_timestamp',
            'file_uploader',
            'file_token',
        ]
