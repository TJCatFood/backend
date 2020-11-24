from django.db import models

# Create your models here.


class QuestionType(models.TextChoices):
    SINGLE = 'SingleAnswer', 'SingleAnswer'
    MULTIPLE = 'MultipleAnswer', 'MultipleAnswer'


class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    publisher_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    chapter = models.IntegerField()
    description = models.CharField(max_length=512)


class AttendQuiz(models.Model):
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    quiz_id = models.ForeignKey('quiz', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()

    class Meta:
        unique_together = (('user_id', 'quiz_id'),)


class QuizQuestion(models.Model):
    quiz_id = models.ForeignKey('quiz', on_delete=models.CASCADE)
    question_id = models.IntegerField()
    question_type = models.IntegerField(
        choices=QuestionType.choices,
        default=QuestionType.SINGLE
    )

    class Meta:
        unique_together = (('quiz_id', 'question_id', 'question_type'),)


class QuizSubmission(models.Model):
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    quiz_id = models.ForeignKey('quiz', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    question_id = models.IntegerField()
    question_type = models.IntegerField(
        choices=QuestionType.choices,
        default=QuestionType.SINGLE
    )
    answer = models.CharField(max_length=16)

    class Meta:
        unique_together = (('user_id', 'quiz_id', 'question_id', 'question_type'),)
