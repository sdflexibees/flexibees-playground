# Generated by Django 3.1.4 on 2021-02-02 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0022_auto_20210201_0643'),
    ]

    operations = [
        migrations.AddField(
            model_name='flexidetails',
            name='selected_country',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]