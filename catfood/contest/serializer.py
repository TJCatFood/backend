from rest_framework.serializers import ModelSerializer
from contest.models import Contest, Match


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
