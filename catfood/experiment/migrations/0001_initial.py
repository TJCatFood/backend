# Generated by Django 3.1.2 on 2020-11-20 17:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course_database', '0001_initial'),
        ('user', '0001_initial'),
        ('class', '0002_auto_20201121_0109'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case_start_timestamp', models.DateTimeField()),
                ('case_end_timestamp', models.DateTimeField()),
                ('case_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_database.experimentcasedatabase')),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class.course')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_file_link', models.CharField(max_length=200)),
                ('submission_timestamp', models.DateTimeField(auto_now=True)),
                ('case_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course_database.experimentcasedatabase')),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class.course')),
                ('submission_uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'unique_together': {('case_id', 'course_id', 'submission_uploader')},
            },
        ),
    ]
