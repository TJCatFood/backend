from django.db import models


class Grade(models.Model):
    #course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    course_id = models.IntegerField()
    student_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    assignment_point = models.IntegerField(null=True)
    exam1_point = models.IntegerField(null=True)
    exam2_point = models.IntegerField(null=True)
    experiment_point = models.IntegerField(null=True)
    contest_point = models.IntegerField(null=True)
    attendance_point = models.IntegerField(null=True)
    bonus_point = models.IntegerField(null=True)
    total_point = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        unique_together = (('student_id', 'course_id'),)


class GradeProportion(models.Model):
    #course_id = models.OneToOneField('course.Course', on_delete=models.CASCADE, primary_key=True)
    course_id = models.IntegerField(primary_key=True)
    assignment = models.PositiveIntegerField(null=True)
    exam1 = models.PositiveIntegerField(null=True)
    exam2 = models.PositiveIntegerField(null=True)
    experiment = models.PositiveIntegerField(null=True)
    contest = models.PositiveIntegerField(null=True)
    attendance = models.PositiveIntegerField(null=True)
