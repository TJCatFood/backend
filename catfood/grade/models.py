from django.db import models


class Grade(models.Model):
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
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
    course_id = models.OneToOneField('class.Course', on_delete=models.CASCADE)
    assignment_point = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    exam1 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    exam2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    experiment = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    contest = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, null=True)
