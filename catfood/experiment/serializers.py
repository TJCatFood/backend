from rest_framework import serializers
from course_database.models import ExperimentCaseDatabase
from experiment.models import CourseCase, ExperimentAssignment
from course.models import Course
class ExperimentCaseDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentCaseDatabase
        fields = [
            'experiment_case_id',
            'experiment_name',
            'experiment_case_name',
            'experiment_case_description',
            'experiment_case_file_token',
            'answer_file_token',
        ]
 
class CourseCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCase
        fields = [
            'case_id',
            'course_id',
            'case_start_timestamp',
            'case_end_timestamp',
            'course_case_id'
        ]

class ExperimentAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentAssignment
        fields = [
            'course_case_id',
            'submission_uploader',
            'submission_file_token',
            'submission_timestamp',
            'submission_score',
            'submission_comments',
            'submission_is_public',
            'submission_case_id'
        ]

