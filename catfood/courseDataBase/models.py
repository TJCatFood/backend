from django.db import models


class CaseBank(models.Model):
    case_id = models.AutoField(primary_key=True)
    experiment_name = models.CharField(max_length=50)
    case_name = models.CharField(max_length=50)
    case_description = models.CharField(max_length=200, null=True)
    case_file_link = models.CharField(max_length=100)
    answer_file_link = models.CharField(max_length=100)
    component_id = models.IntegerField


class CourseDocument(models.Model):
    file_course_document_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    file_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    file_usage = models.CharField(max_length=100)
    file_timestamp = models.DateTimeField(auto_now=True)
    file_comment = models.CharField(max_length=200)
    file_link = models.CharField(max_length=200)


class questionBank(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_chapter = models.IntegerField
    question_content = models.CharField(max_length=100)
    question_choice_a_content = models.CharField(max_length=20)
    question_choice_b_content = models.CharField(max_length=20)
    question_choice_c_content = models.CharField(max_length=20)
    question_choice_d_content = models.CharField(max_length=20)
    question_answer = models.CharField(max_length=20)
