# Generated by Django 3.1.4 on 2021-04-05 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0021_remove_employmentdetail_employment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='employmentdetail',
            name='employment_type',
            field=models.PositiveIntegerField(choices=[(1, 'Full Time Employee'), (2, 'Full Time Contractor'), (3, 'Part Time Employee'), (4, 'Part Time Contractor'), (5, 'Consultant'), (6, 'Paid Internship'), (7, 'Unpaid Internship')], default=1),
        ),
    ]
