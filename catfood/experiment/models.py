from django.db import models

# Create your models here.


class ExperimentAssignment(models.Model):
    course_case_id = models.ForeignKey('CourseCase', on_delete=models.CASCADE)
    submission_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    submission_file_token = models.CharField(max_length=200)
    submission_timestamp = models.DateTimeField(auto_now=True)
    submission_score = models.IntegerField(default=-1)
    submission_comments = models.CharField(max_length=1024, blank=True)
    submission_is_public = models.BooleanField(default=False)
    submission_case_id = models.AutoField(primary_key=True)

    class Meta:
        unique_together = (('course_case_id', 'submission_uploader'),)


class CourseCase(models.Model):
    case_id = models.ForeignKey('course_database.ExperimentCaseDatabase', on_delete=models.CASCADE)
    course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    case_start_timestamp = models.DateTimeField()
    case_end_timestamp = models.DateTimeField()
    course_case_id = models.AutoField(primary_key=True)

    class Meta:
        unique_together = (('case_id', 'course_id'),)
