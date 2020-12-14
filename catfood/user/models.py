from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

user_character = ((1, 'is_charging_teacher'), (2, 'is_teacher'),
                  (3, 'is_teaching_assistant'), (4, 'is_student'))


class UserManager(BaseUserManager):
    def create(self, password, realname, university_id,
               school_id, character, personal_id, avatar=None, email=None):
        university = University.objects.get(university_id=university_id)
        school = School.objects.get(school_id=school_id)
        if avatar is None:
            avatar = ''
        if email is None:
            email = ''
        user = self.model(
            realname=realname,
            email=User.objects.normalize_email(email),
            university_id=university,
            school_id=school,
            personal_id=personal_id,
            character=character,
            avatar=avatar,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    # AbstractBaseUser already has password.
    realname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    university_id = models.ForeignKey('University', on_delete=models.CASCADE)
    school_id = models.ForeignKey('School', on_delete=models.CASCADE)
    character = models.IntegerField(choices=user_character, default=4)
    personal_id = models.CharField(max_length=20)
    avatar = models.CharField(max_length=50)
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['password']
    objects = UserManager()


class University(models.Model):
    university_id = models.AutoField(primary_key=True)
    official_id = models.CharField(max_length=20, default=0)
    university_name = models.CharField(max_length=50)


class School(models.Model):
    school_id = models.AutoField(primary_key=True)
    school_name = models.CharField(max_length=50)
    university_id = models.ForeignKey('University', on_delete=models.CASCADE)


class TakeCourse(models.Model):
    student_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = (('student_id', 'course_id'),)


class Invitation(models.Model):
    invitor_id = models.ForeignKey('User', on_delete=models.CASCADE)
    course_id = models.ForeignKey('course.Course', on_delete=models.CASCADE)
    email = models.EmailField(max_length=50)
    invitee_name = models.CharField(max_length=200, null=True)

    class Meta:
        unique_together = (('invitor_id', 'course_id', 'email'),)
