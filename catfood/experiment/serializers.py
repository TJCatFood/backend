from rest_framework import serializers
from course_database.models import ExperimentCaseDatabase

class ExperimentCaseDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentCaseDatabase
        fields = [
            'experiment_case_id',
            'experiment_name',
            'experiment_case_name',
            'experiment_case_description',
            'experiment_case_file_token',
            'answer_file_token'
        ]
 