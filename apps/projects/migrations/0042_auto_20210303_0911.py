# Generated by Django 3.1.4 on 2021-03-03 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0041_auto_20210303_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suspended',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
