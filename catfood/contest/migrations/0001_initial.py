# Generated by Django 3.1.2 on 2020-12-10 05:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('class', '0002_auto_20201210_1311'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('contest_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100, null=True)),
                ('participant_number', models.IntegerField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('chapter', models.IntegerField()),
                ('description', models.CharField(max_length=512)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class.course')),
                ('publisher_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('match_id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('contest_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.contest')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContestSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('question_id', models.IntegerField()),
                ('question_type', models.IntegerField(choices=[('SingleAnswer', 'SingleAnswer'), ('MultipleAnswer', 'MultipleAnswer')], default='SingleAnswer')),
                ('answer', models.CharField(max_length=16)),
                ('contest_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.contest')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user_id', 'contest_id', 'question_id', 'question_type')},
            },
        ),
        migrations.CreateModel(
            name='ContestQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_id', models.IntegerField()),
                ('question_type', models.IntegerField(choices=[('SingleAnswer', 'SingleAnswer'), ('MultipleAnswer', 'MultipleAnswer')], default='SingleAnswer')),
                ('contest_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.contest')),
            ],
            options={
                'unique_together': {('contest_id', 'question_id', 'question_type')},
            },
        ),
        migrations.CreateModel(
            name='AttendContest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('score', models.IntegerField()),
                ('rank', models.IntegerField()),
                ('contest_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.contest')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user_id', 'contest_id')},
            },
        ),
    ]
