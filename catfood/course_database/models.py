from django.db import models


class ExperimentCaseDatabase(models.Model):
    experiment_case_id = models.AutoField(primary_key=True)
    experiment_name = models.CharField(max_length=50)
    experiment_case_name = models.CharField(max_length=50)
    experiment_case_description = models.CharField(max_length=1024, null=True)
    experiment_case_file_token = models.CharField(max_length=256)
    answer_file_token = models.CharField(max_length=256)
    case_created_timestamp = models.DateTimeField(auto_now_add=True)


class CourseDocument(models.Model):
    file_course_document_id = models.AutoField(primary_key=True)
    # FIXME: change back when course module completed
    # course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    course_id = models.IntegerField()
    file_display_name = models.CharField(max_length=1024)
    file_comment = models.CharField(max_length=1024)
    file_create_timestamp = models.DateTimeField(auto_now=True)
    file_update_timestamp = models.DateTimeField(auto_now=True)
    # FIXME: change back when course module completed
    # file_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    file_uploader = models.IntegerField()
    file_token = models.CharField(max_length=200)

class ExperimentDocument(models.Model):
    file_course_document_id = models.AutoField(primary_key=True)
    # FIXME: change back when experiment module completed
    # experiment_id = ?
    experiment_id = models.IntegerField()
    file_display_name = models.CharField(max_length=1024)
    file_comment = models.CharField(max_length=1024)
    file_create_timestamp = models.DateTimeField(auto_now=True)
    file_update_timestamp = models.DateTimeField(auto_now=True)
    # FIXME: change back when course module completed
    # file_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    file_uploader = models.IntegerField()
    file_token = models.CharField(max_length=200)


class SingleChoiceQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_chapter = models.IntegerField()
    question_content = models.CharField(max_length=100)
    question_choice_a_content = models.CharField(max_length=256)
    question_choice_b_content = models.CharField(max_length=256)
    question_choice_c_content = models.CharField(max_length=256)
    question_choice_d_content = models.CharField(max_length=256)
    question_answer = models.CharField(max_length=20)


class MultipleChoiceQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_chapter = models.IntegerField()
    question_content = models.CharField(max_length=100)
    question_choice_a_content = models.CharField(max_length=256)
    question_choice_b_content = models.CharField(max_length=256)
    question_choice_c_content = models.CharField(max_length=256)
    question_choice_d_content = models.CharField(max_length=256)
    question_answer = models.CharField(max_length=20)
