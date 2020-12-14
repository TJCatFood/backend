# Generated by Django 3.1.2 on 2020-12-13 06:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='University',
            fields=[
                ('university_id', models.AutoField(primary_key=True, serialize=False)),
                ('official_id', models.CharField(default=0, max_length=20)),
                ('university_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('school_id', models.AutoField(primary_key=True, serialize=False)),
                ('school_name', models.CharField(max_length=50)),
                ('university_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.university')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('realname', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('character', models.IntegerField(choices=[(1, 'is_charging_teacher'), (2, 'is_teacher'), (3, 'is_teaching_assistant'), (4, 'is_student')], default=4)),
                ('personal_id', models.CharField(max_length=20)),
                ('avatar', models.CharField(max_length=50)),
                ('school_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.school')),
                ('university_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.university')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TakeCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=False)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student_id', 'course_id')},
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=50)),
                ('invitee_name', models.CharField(max_length=200, null=True)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course')),
                ('invitor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('invitor_id', 'course_id', 'email')},
            },
        ),
    ]
