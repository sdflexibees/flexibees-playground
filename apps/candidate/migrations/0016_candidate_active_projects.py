# Generated by Django 3.1.4 on 2021-03-21 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0015_candidate_legacy_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='active_projects',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
