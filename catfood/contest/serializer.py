from rest_framework.serializers import ModelSerializer
from contest.models import Contest, Match, ContestQuestion


class ContestSerializer(ModelSerializer):
    class Meta:
        model = Contest
        fields = [
            'contest_id',
            'course_id',
            'publisher_id',
            'title',
            'participant_number',
            'start_time',
            'end_time',
            'chapter',
            'description'
        ]


class MatchSerializer(ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'match_id',
            'contest_id',
            'user_id',
            'timestamp'
        ]


class ContestQuestionSerializer(ModelSerializer):
    class Meta:
        model = ContestQuestion
        fields = [
            'contest_id',
            'question_id',
            'question_type'
        ]
