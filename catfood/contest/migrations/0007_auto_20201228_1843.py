# Generated by Django 3.1.2 on 2020-12-28 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0006_auto_20201224_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestsubmission',
            name='answer',
            field=models.CharField(blank=True, max_length=16),
        ),
    ]
