from django.contrib.auth.models import User as BaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

user_character = ((1, 'is_charging_teacher'), (2, 'is_teacher'), (3, 'is_teaching_assistant'), (4, 'is_student'))


class UserManager(BaseUserManager):
    def create(self, user_id, password=None, realname=None):
        """
        Creates and saves a User with the given email, realname and password.
        """
        if not user_id:
            raise ValueError('Users must have a user_id')

        user = self.model(
            user_id=user_id,
            realname=realname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_id = models.CharField(max_length=50, primary_key=True)
    # password_digest = models.CharField(max_length=50)
    realname = models.CharField(max_length=50)
    personal_id = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    university_id = models.IntegerField(default=0)
    school_id = models.IntegerField(default=0)
    character = models.IntegerField(choices=user_character, default=4)
    avatar = models.CharField(max_length=50)
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['password']
    objects = UserManager()


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
