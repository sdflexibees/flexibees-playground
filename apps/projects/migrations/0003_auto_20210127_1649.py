# Generated by Django 3.1.4 on 2021-01-27 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20210127_0631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flexidetails',
            name='max_no_of_working_hours',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='flexidetails',
            name='min_no_of_working_hours',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.IntegerField(choices=[(1, 'Project Proposal'), (2, 'Project Details Updated'), (3, 'Candidate Salary Requested'), (4, 'Candidate Salary Proposed'), (5, 'Project Pricing to Client Updated'), (6, 'Project Details Updated'), (7, 'New'), (8, 'In Progress'), (9, 'Closed'), (10, 'Re-opened'), (11, 'Suspended')], default=1),
        ),
    ]