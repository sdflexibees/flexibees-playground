# Generated by Django 3.1.4 on 2021-02-05 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0032_auto_20210205_0333'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='suspended_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
