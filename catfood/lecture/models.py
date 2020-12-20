from django.db import models


class Homework(models.Model):
    homework_id = models.AutoField(primary_key=True)
    # FIXME: change back when course module completed
    # course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    course_id = models.IntegerField()
    # FIXME: change back when user module completed
    # homework_creator = models.ForeignKey('user.User', on_delete=models.CASCADE)
    homework_creator = models.IntegerField()
    homework_title = models.CharField(max_length=128)
    homework_description = models.CharField(max_length=1024)
    homework_start_timestamp = models.DateTimeField()
    homework_end_timestamp = models.DateTimeField()
    homework_create_timestamp = models.DateTimeField()
    homework_update_timestamp = models.DateTimeField()


class HomeworkScore(models.Model):
    class Meta:
        managed = False
    homework_id = models.ForeignKey('Homework', on_delete=models.DO_NOTHING)
    # FIXME: change back when user module completed
    # student_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    student_id = models.IntegerField()
    # FIXME: change back when course module completed
    # course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    course_id = models.IntegerField()
    homework_teachers_comments = models.CharField(max_length=2048)
    homework_is_grade_available_to_students = models.BooleanField(default=False)
    homework_score = models.IntegerField()


class HomeworkFile(models.Model):
    file_homework_id = models.AutoField(primary_key=True)
    homework_id = models.ForeignKey('Homework', on_delete=models.DO_NOTHING)
    # FIXME: change back when user module completed
    # file_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    file_display_name = models.CharField(max_length=1024)
    file_comment = models.CharField(max_length=1024)
    file_uploader = models.IntegerField()
    file_timestamp = models.DateField(auto_now=True)
    file_token = models.CharField(max_length=200)


class CourseChapterDescrption(models.Model):
    course_chapter_description_id = models.AutoField(primary_key=True)
    # FIXME: change back when course module completed
    # course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    course_id = models.IntegerField()
    course_chapter_id = models.IntegerField()
    course_chapter_title = models.CharField(max_length=64)
    course_chapter_mooc_link = models.CharField(max_length=200)
