from django.db import models


class ExperimentCaseDatabase(models.Model):
    experiment_case_id = models.AutoField(primary_key=True)
    experiment_name = models.CharField(max_length=50)
    experiment_case_name = models.CharField(max_length=50)
    experiment_case_description = models.CharField(max_length=1024, null=True)
    experiment_case_file_link = models.CharField(max_length=256)
    answer_file_link = models.CharField(max_length=256)
    component_id = models.IntegerField()


class CourseDocument(models.Model):
    file_course_document_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    file_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE)
    file_usage = models.CharField(max_length=100)
    file_timestamp = models.DateTimeField(auto_now=True)
    file_comment = models.CharField(max_length=1024)
    file_link = models.CharField(max_length=200)


class choiceSingleQuestionDatabase(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_chapter = models.IntegerField()
    question_content = models.CharField(max_length=100)
    question_choice_a_content = models.CharField(max_length=256)
    question_choice_b_content = models.CharField(max_length=256)
    question_choice_c_content = models.CharField(max_length=256)
    question_choice_d_content = models.CharField(max_length=256)
    question_answer = models.CharField(max_length=20)


class choiceMultipleQuestionDatabase(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_chapter = models.IntegerField()
    question_content = models.CharField(max_length=100)
    question_choice_a_content = models.CharField(max_length=256)
    question_choice_b_content = models.CharField(max_length=256)
    question_choice_c_content = models.CharField(max_length=256)
    question_choice_d_content = models.CharField(max_length=256)
    question_answer = models.CharField(max_length=20)
