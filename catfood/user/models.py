from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django import forms



class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    # AbstractBaseUser seems to have this.
    # password_digest = models.CharField(max_length=50)
    realname = models.CharField(max_length=50)
    personal_id = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    university_id = models.IntegerField()
    school_id = models.IntegerField()
    character = models.IntegerField()
    avatar = models.CharField(max_length=50)
    REQUIRED_FIELDS = ['password']
    USERNAME_FIELD = 'user_id'


class University(models.Model):
    university_id = models.AutoField(primary_key=True)
    university_name = models.CharField(max_length=50)


class School(models.Model):
    school_id = models.AutoField(primary_key=True)
    school_name = models.CharField(max_length=50)
    university_id = models.ForeignKey('University', on_delete=models.CASCADE)


class TakeCourse(models.Model):
    student_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = (('student_id', 'course_id'),)


class Invitation(models.Model):
    invitor_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    email = models.EmailField(max_length=50)
    invitee_name = models.CharField(max_length=200, null=True)

    class Meta:
        unique_together = (('invitor_id', 'course_id', 'email'),)
