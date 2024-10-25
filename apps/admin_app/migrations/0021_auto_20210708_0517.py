# Generated by Django 3.1.4 on 2021-07-08 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0020_appversion'),
    ]

    operations = [
        migrations.AddField(
            model_name='appversion',
            name='force_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appversion',
            name='recommended_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appversion',
            name='under_maintenance',
            field=models.BooleanField(default=False),
        ),
    ]
