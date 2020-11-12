from django.db import models


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_creator_school_id = models.CharField(max_length=50)
    course_name = models.CharField(max_length=50)
    course_description = models.CharField(max_length=200, null=True)
    course_credit = models.IntegerField(default=0)
    course_study_time_needed = models.IntegerField
    course_type = models.BooleanField(default=True)
    course_start_timestamp = models.DateTimeField()
    course_end_timestamp = models.DateTimeField()
    course_avatar = models.CharField(max_length=100)


class Teach(models.Model):
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    teacher_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    role = models.IntegerField(default=2)  # 0责任教师 1普通教师 2助教

    class Meta:
        unique_together = (('teacher_id', 'course_id'),)


# class ExperimentAssignment(models.Model):
