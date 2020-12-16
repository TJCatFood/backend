from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'announcement_id',
            'course_id',
            'announcement_title',
            'announcement_contents',
            'announcement_is_pinned',
            'announcement_publish_time',
            'announcement_last_update_time',
            'announcement_sender_id',
        ]
