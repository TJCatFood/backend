# Generated by Django 3.1.2 on 2020-12-23 00:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0002_auto_20201219_1935'),
        ('contest', '0004_auto_20201221_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendcontest',
            name='contest_id',
            field=models.ForeignKey(db_column='contest_id', on_delete=django.db.models.deletion.CASCADE, related_name='contest_id+', to='contest.contest'),
        ),
        migrations.AlterField(
            model_name='attendcontest',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='user_id+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contest',
            name='course_id',
            field=models.ForeignKey(db_column='course_id', on_delete=django.db.models.deletion.CASCADE, related_name='course_id+', to='course.course'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='publisher_id',
            field=models.ForeignKey(db_column='publisher_id', on_delete=django.db.models.deletion.CASCADE, related_name='publisher_id+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contestquestion',
            name='contest_id',
            field=models.ForeignKey(db_column='contest_id', on_delete=django.db.models.deletion.CASCADE, related_name='contest_id+', to='contest.contest'),
        ),
        migrations.AlterField(
            model_name='contestsubmission',
            name='contest_id',
            field=models.ForeignKey(db_column='contest_id', on_delete=django.db.models.deletion.CASCADE, related_name='contest_id+', to='contest.contest'),
        ),
        migrations.AlterField(
            model_name='contestsubmission',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='user_id+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='match',
            name='contest_id',
            field=models.ForeignKey(db_column='contest_id', on_delete=django.db.models.deletion.CASCADE, related_name='contest_id+', to='contest.contest'),
        ),
        migrations.AlterField(
            model_name='match',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='user_id+', to=settings.AUTH_USER_MODEL),
        ),
    ]
