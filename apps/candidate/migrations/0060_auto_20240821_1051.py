# Generated by Django 3.1.4 on 2024-08-21 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0025_auto_20231009_1217'),
        ('employer', '0007_auto_20240821_1051'),
        ('candidate', '0059_candidate_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientfeedback',
            name='job_interview',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employer.interview'),
        ),
        migrations.AlterField(
            model_name='clientfeedback',
            name='feedback_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='admin_app.adminuser'),
        ),
        migrations.AlterField(
            model_name='clientfeedback',
            name='final_selection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='candidate.finalselection'),
        ),
    ]