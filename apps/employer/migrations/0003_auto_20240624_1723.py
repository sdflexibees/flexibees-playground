# Generated by Django 3.1.4 on 2024-06-24 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0002_auto_20240624_0705'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobcustomroleskills',
            old_name='skills',
            new_name='skill',
        ),
    ]
