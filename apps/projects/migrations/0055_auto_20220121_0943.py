# Generated by Django 3.1.4 on 2022-01-21 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0054_auto_20220121_0737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='role_type',
            field=models.CharField(blank=True, max_length=120),
        ),
    ]