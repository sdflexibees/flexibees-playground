# Generated by Django 3.1.4 on 2021-04-09 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0027_auto_20210409_0649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certification',
            name='description',
        ),
        migrations.RemoveField(
            model_name='certification',
            name='expiry_date',
        ),
        migrations.RemoveField(
            model_name='certification',
            name='issue_date',
        ),
        migrations.RemoveField(
            model_name='certification',
            name='no_expiry',
        ),
        migrations.RemoveField(
            model_name='education',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='education',
            name='start_date',
        ),
        migrations.AlterField(
            model_name='candidateattachment',
            name='attachment',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='education',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='education',
            name='grade',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
