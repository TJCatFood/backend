from django.db import models

# Create your models here.


class QuestionType(models.IntegerChoices):
    SINGLE = 0
    MULTIPLE = 1


class Contest(models.Model):
    contest_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name='course_id+', db_column='course_id')
    publisher_id = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='publisher_id+', db_column='publisher_id')
    title = models.CharField(max_length=100, null=True)
    participant_number = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    chapter = models.IntegerField()
    description = models.CharField(max_length=512)


class AttendContest(models.Model):
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user_id+', db_column='user_id')
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE, related_name='contest_id+', db_column='contest_id')
    timestamp = models.DateTimeField()
    score = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        unique_together = (('user_id', 'contest_id'),)


class ContestQuestion(models.Model):
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE, related_name='contest_id+', db_column='contest_id')
    question_id = models.IntegerField()
    question_type = models.IntegerField(
        choices=QuestionType.choices,
        default=QuestionType.SINGLE
    )

    class Meta:
        unique_together = (('contest_id', 'question_id', 'question_type'),)


class Match(models.Model):
    match_id = models.AutoField(primary_key=True)
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE, related_name='contest_id+', db_column='contest_id')
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user_id+', db_column='user_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    match_tag = models.IntegerField(default=0)


class ContestSubmission(models.Model):
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user_id+', db_column='user_id')
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE, related_name='contest_id+', db_column='contest_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    question_id = models.IntegerField()
    question_type = models.IntegerField(
        choices=QuestionType.choices,
        default=QuestionType.SINGLE
    )
    answer = models.CharField(max_length=16, blank=True)

    class Meta:
        unique_together = (('user_id', 'contest_id', 'question_id', 'question_type'),)
