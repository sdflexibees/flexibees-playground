# Generated by Django 3.1.4 on 2021-05-21 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('availability', '0002_auto_20210521_0613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitycard',
            name='priority',
        ),
        migrations.AddField(
            model_name='activitycard',
            name='admin_priority',
            field=models.JSONField(blank=True, default={'afternoon': 'low', 'evening': 'low', 'morning': 'low', 'night': 'low'}),
        ),
        migrations.AlterField(
            model_name='activitycard',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]