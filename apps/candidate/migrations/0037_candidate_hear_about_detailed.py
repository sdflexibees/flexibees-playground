# Generated by Django 3.1.4 on 2021-04-23 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0036_candidate_read_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='hear_about_detailed',
            field=models.TextField(blank=True, null=True),
        ),
    ]
