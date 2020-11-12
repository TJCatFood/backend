# Generated by Django 3.1.2 on 2020-11-12 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('class', '0002_auto_20201112_2027'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradeProportion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignmentPoint', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('exam1', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('exam2', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('experiment', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('combat', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('attendance', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('course_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='class.course')),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignmentPoint', models.IntegerField(null=True)),
                ('exam1Point', models.IntegerField(null=True)),
                ('exam2Point', models.IntegerField(null=True)),
                ('experimentPoint', models.IntegerField(null=True)),
                ('contestPoint', models.IntegerField(null=True)),
                ('attendancePoint', models.IntegerField(null=True)),
                ('bonusPoint', models.IntegerField(null=True)),
                ('totalPoint', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class.course')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'unique_together': {('student_id', 'course_id')},
            },
        ),
    ]
