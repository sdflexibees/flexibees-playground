# Generated by Django 3.1.4 on 2021-01-30 07:29

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0020_remove_requirement_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirement',
            name='language',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20), default=list, size=None),
        ),
    ]