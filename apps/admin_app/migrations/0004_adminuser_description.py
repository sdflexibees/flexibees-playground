# Generated by Django 3.1.4 on 2021-01-06 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0003_auto_20210106_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminuser',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]