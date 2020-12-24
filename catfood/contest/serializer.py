from rest_framework.serializers import ModelSerializer
from contest.models import Contest, Match, ContestQuestion, AttendContest


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
            'timestamp',
            'match_tag'
        ]


class ContestQuestionSerializer(ModelSerializer):
    class Meta:
        model = ContestQuestion
        fields = [
            'contest_id',
            'question_id',
            'question_type'
        ]


class AttendSerializer(ModelSerializer):
    class Meta:
        model = AttendContest
        fields = [
            'user_id',
            'contest_id',
            'timestamp',
            'score',
            'rank'
        ]
