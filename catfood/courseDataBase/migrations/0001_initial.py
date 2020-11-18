# Generated by Django 3.1.2 on 2020-11-18 02:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('class', '0002_auto_20201118_1028'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExperimentCaseDataBase',
            fields=[
                ('experiment_case_id', models.AutoField(primary_key=True, serialize=False)),
                ('experiment_name', models.CharField(max_length=50)),
                ('experiment_case_name', models.CharField(max_length=50)),
                ('experiment_case_description', models.CharField(max_length=1024, null=True)),
                ('experiment_case_file_link', models.CharField(max_length=256)),
                ('answer_file_link', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='questionBank',
            fields=[
                ('question_id', models.AutoField(primary_key=True, serialize=False)),
                ('question_content', models.CharField(max_length=100)),
                ('question_choice_a_content', models.CharField(max_length=256)),
                ('question_choice_b_content', models.CharField(max_length=256)),
                ('question_choice_c_content', models.CharField(max_length=256)),
                ('question_choice_d_content', models.CharField(max_length=256)),
                ('question_answer', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CourseDocument',
            fields=[
                ('file_course_document_id', models.AutoField(primary_key=True, serialize=False)),
                ('file_usage', models.CharField(max_length=100)),
                ('file_timestamp', models.DateTimeField(auto_now=True)),
                ('file_comment', models.CharField(max_length=1024)),
                ('file_link', models.CharField(max_length=200)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class.course')),
                ('file_uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
    ]
