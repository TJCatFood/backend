# Generated by Django 3.1.2 on 2020-12-07 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttendContest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('score', models.IntegerField()),
                ('rank', models.IntegerField()),
            ],
        ),
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
            ],
        ),
        migrations.CreateModel(
            name='ContestQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_id', models.IntegerField()),
                ('question_type', models.IntegerField(choices=[('SingleAnswer', 'SingleAnswer'), ('MultipleAnswer', 'MultipleAnswer')], default='SingleAnswer')),
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
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('match_id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('contest_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.contest')),
            ],
        ),
    ]
