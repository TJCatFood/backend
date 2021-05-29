from django.db import models


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_creator_school_id = models.CharField(max_length=50)
    course_name = models.CharField(max_length=50)
    course_description = models.CharField(max_length=512, null=True)
    course_credit = models.IntegerField(default=0)
    course_study_time_needed = models.IntegerField(default=0)
    course_type = models.CharField(max_length=20)
    course_start_time = models.DateTimeField()
    course_end_time = models.DateTimeField()
    course_avatar = models.CharField(max_length=100)
    course_is_score_public = models.BooleanField(default=False)


class Teach(models.Model):
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    teacher_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    course_teach_id = models.AutoField(primary_key=True)

    class Meta:
        unique_together = (('teacher_id', 'course_id'),)
