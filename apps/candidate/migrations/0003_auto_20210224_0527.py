# Generated by Django 3.1.4 on 2021-02-24 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0019_adminuser_active_projects'),
        ('candidate', '0002_auto_20210223_1634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='role',
        ),
        migrations.AddField(
            model_name='candidate',
            name='roles',
            field=models.ManyToManyField(blank=True, to='admin_app.Role'),
        ),
    ]
