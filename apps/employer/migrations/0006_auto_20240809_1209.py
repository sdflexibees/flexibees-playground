# Generated by Django 3.1.4 on 2024-08-09 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0005_candidatejobnotes_candidatejobstatus_employerinterviewslot_interviewfeedback_skippedcandidate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.CharField(blank=True, choices=[('1', 'Created'), ('2', 'Candidate shortlisted'), ('3', 'candidate shown interest'), ('4', 'Candidate Interview scheduled'), ('5', 'Interview cleared'), ('6', 'Finally Selected'), ('7', 'Project Confirmed'), ('8', 'Contract Pending'), ('9', 'Offered'), ('10', 'Accepted'), ('11', 'In Project'), ('12', 'Project Canceled'), ('13', 'Pending Renewal'), ('14', 'Withdrawn'), ('15', 'Dropped off')], default='1', max_length=5),
        ),
    ]
