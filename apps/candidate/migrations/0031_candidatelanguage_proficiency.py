# Generated by Django 3.1.4 on 2021-04-14 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0030_remove_candidatelanguage_proficiency'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidatelanguage',
            name='proficiency',
            field=models.IntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced'), (4, 'Expert')], default=1),
        ),
    ]