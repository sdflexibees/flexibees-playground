# Generated by Django 3.1.4 on 2021-04-05 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0024_employmentdetail_employment_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employmentdetail',
            name='industry_type',
        ),
    ]