from django.db import models

# Create your models here.


class ExperimentAssignment(models.Model):
    case_id = models.ForeignKey('course_database.ExperimentCase', on_delete=models.CASCADE)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    submission_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    submission_file_link = models.CharField(max_length=200)
    submission_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('case_id', 'course_id', 'submission_uploader'),)


class CourseCase(models.Model):
    case_id = models.ForeignKey('course_database.ExperimentCase', on_delete=models.CASCADE)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    case_start_timestamp = models.DateTimeField()
    case_end_timestamp = models.DateTimeField()
