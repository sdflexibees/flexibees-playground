# Generated by Django 3.1.4 on 2024-08-22 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0007_auto_20240821_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='status',
            field=models.CharField(choices=[('1', 'Scheduled'), ('2', 'Cleared'), ('3', 'Rejected')], max_length=3),
        ),
    ]