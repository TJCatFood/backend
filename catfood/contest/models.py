from django.db import models

# Create your models here.


class Contest(models.Model):
    contest_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    publisher_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True)
    participant_number = models.IntegerField()
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    chapter = models.IntegerField()
    description = models.CharField(max_length=200)


class Attend(models.Model):
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    score = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        unique_together = (('user_id', 'contest_id'),)


class ContestQuestion(models.Model):
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE)
    question_id = models.ForeignKey('courseDataBase.questionBank', on_delete=models.CASCADE)
    question_type = models.IntegerField(default=0)

    class Meta:
        unique_together = (('contest_id', 'question_id'),)


class Match(models.Model):
    mathch_id = models.AutoField(primary_key=True)
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE)
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()


class Submission(models.Model):
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    contest_id = models.ForeignKey('Contest', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    question_id = models.ForeignKey('courseDataBase.questionBank', on_delete=models.CASCADE)
    question_type = models.IntegerField(default=0)
    answer = models.CharField(max_length=300)

    class Meta:
        unique_together = (('user_id', 'contest_id', 'question_id'),)
