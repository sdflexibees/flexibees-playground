# Generated by Django 3.1.4 on 2024-07-30 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_users_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='profile_image',
            field=models.URLField(null=True),
        ),
    ]