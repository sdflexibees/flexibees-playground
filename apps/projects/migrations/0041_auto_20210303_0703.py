# Generated by Django 3.1.4 on 2021-03-03 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0040_project_notify_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricing',
            name='comments',
            field=models.TextField(blank=True),
        ),
    ]