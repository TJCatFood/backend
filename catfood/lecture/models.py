from django.db import models


class FileUsage(models.TextChoices):
    EXPERIMENT = 'Experiment', 'Experiment'
    LECTURE = 'Lecture', 'Lecture'


class HomeworkList(models.Model):
    homework_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    homework_creator = models.ForeignKey('user.User', on_delete=models.CASCADE)
    homework_description = models.CharField(max_length=1024)
    homework_attachment_link = models.CharField(max_length=200)
    homework_start_timestamp = models.DateTimeField()


class HomeworkScoreList(models.Model):
    homework_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    homework_student_grade = models.IntegerField()
    homework_teachers_comments = models.CharField(max_length=2048)
    homework_is_grade_available_to_students = models.BooleanField(default=False)


class HomeworkFileList(models.Model):
    file_homework_id = models.AutoField(primary_key=True)
    homework_id = models.ForeignKey('HomeworkList', on_delete=models.CASCADE)
    file_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    file_usage = models.CharField(
        max_length=100,
        choices=FileUsage.choices
    )
    file_timestamp = models.DateField(auto_now=True)
    file_link = models.CharField(max_length=200)
