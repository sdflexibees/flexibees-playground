# Generated by Django 3.1.4 on 2021-02-23 06:04

import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admin_app', '0019_adminuser_active_projects'),
        ('projects', '0039_auto_20210219_0445'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Assignment not submitted'), (2, 'Assignment submitted'), (3, 'Assignment not cleared'), (4, 'Assignment cleared'), (5, 'Assignment on hold'), (6, 'No assignment')], default=1)),
                ('submitted_assignment', models.URLField(null=True)),
                ('submitted_date', models.DateTimeField(blank=True, null=True)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Please Enter correct Contact no.', regex='^\\d{7,15}$')])),
                ('password', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('will_to_travel_to_local_office', models.BooleanField(default=False)),
                ('hear_about_flexibees', models.CharField(choices=[('others', 'others')], max_length=50)),
                ('brief_description', models.TextField()),
                ('profile_description', models.TextField()),
                ('employment_details', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('education', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('certifications', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('languages', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('attachment', models.URLField(null=True)),
                ('total_year_of_experience', models.IntegerField(blank=True, null=True)),
                ('relevant_experience', models.IntegerField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.role')),
                ('skills', models.ManyToManyField(blank=True, to='admin_app.Skill')),
            ],
        ),
        migrations.CreateModel(
            name='Flexifit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Flexifit interview scheduled'), (2, 'Candidate selected'), (3, 'Candidate not selected'), (4, 'Flexifit on hold')], default=1)),
                ('scheduled_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='Functional',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Functional interview scheduled'), (2, 'Functional interview cleared'), (3, 'Functional interview not cleared'), (4, 'Functional on hold')], default=1)),
                ('scheduled_date', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='Shortlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Notification not sent'), (2, 'Notification sent/Waiting for response')], default=1)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='InterestCheckAndSelfEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Interested, Self evaluation not done'), (2, 'Interested, Self evaluation done'), (3, 'Not interested')])),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='FunctionalFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skills_feedback', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('overall_score', models.IntegerField(default=0)),
                ('recommendation', models.CharField(max_length=150)),
                ('comments', models.TextField()),
                ('interview_summary', models.URLField(null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('feedback_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.adminuser')),
                ('functional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.functional')),
            ],
        ),
        migrations.CreateModel(
            name='FlexifitFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recommendation', models.CharField(max_length=150)),
                ('comments', models.TextField()),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('feedback_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.adminuser')),
                ('flexifit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.flexifit')),
            ],
        ),
        migrations.CreateModel(
            name='FinalSelection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Flexibees selected'), (2, 'Sent to BD manager'), (3, 'Client selected'), (4, 'Client rejected')], default=1)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate')),
                ('flexifit_feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.flexifitfeedback')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='ClientFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recommendation', models.CharField(max_length=150)),
                ('comments', models.TextField()),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('feedback_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.adminuser')),
                ('final_selection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.finalselection')),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recommendation', models.CharField(max_length=150)),
                ('comments', models.TextField()),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.assignment')),
                ('feedback_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.adminuser')),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project'),
        ),
    ]