# Generated by Django 3.1.4 on 2024-10-25 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_rolemapping_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='user_type',
            field=models.CharField(choices=[('1', 'Employer'), ('2', 'Candidate')], default='1', max_length=2),
        ),
    ]
