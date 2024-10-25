# Generated by Django 3.1.4 on 2021-01-29 07:49

import core.extra
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_auto_20210129_0552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flexidetails',
            name='assignment_file',
            field=models.FileField(null=True, upload_to=core.extra.upload_file),
        ),
        migrations.AlterField(
            model_name='flexidetails',
            name='company_address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='flexidetails',
            name='how_often_travelling',
            field=models.CharField(blank=True, max_length=25),
        ),
        migrations.AlterField(
            model_name='flexidetails',
            name='project_duration_unit',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='flexidetails',
            name='selected_city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='flexidetails',
            name='turn_around_duration_unit',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='flexidetails',
            name='working_hours_duration_unit',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
