# Generated by Django 3.1.4 on 2021-06-03 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0041_candidate_mylife_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='profile_last_updated',
            field=models.DateTimeField(null=True),
        ),
    ]