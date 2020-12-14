from rest_framework import serializers
from .models import CourseChapterDescrption


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
