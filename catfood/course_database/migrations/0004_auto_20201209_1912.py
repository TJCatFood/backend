# Generated by Django 3.1.2 on 2020-12-09 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course_database', '0003_experimentcase_component_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursedocument',
            name='course_id',
        ),
        migrations.RemoveField(
            model_name='coursedocument',
            name='file_uploader',
        ),
    ]
