# Generated by Django 3.1.2 on 2020-12-20 06:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lecture', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homeworkfile',
            name='file_usage',
        ),
    ]