# Generated by Django 3.1.4 on 2021-01-27 06:31

import core.extra
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0014_zohotoken'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_website', models.URLField(blank=True, null=True)),
                ('company_brief', models.TextField()),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FlexiDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_constraints', models.BooleanField(default=False)),
                ('selected_city', models.CharField(max_length=100)),
                ('is_travel_required', models.BooleanField(default=False)),
                ('how_often_travelling', models.CharField(max_length=25)),
                ('company_address', models.TextField()),
                ('min_no_of_working_hours', models.IntegerField()),
                ('max_no_of_working_hours', models.IntegerField()),
                ('working_hours_duration_unit', models.CharField(max_length=10)),
                ('project_duration', models.IntegerField()),
                ('project_duration_unit', models.CharField(max_length=10)),
                ('turn_around_time', models.IntegerField()),
                ('turn_around_duration_unit', models.CharField(max_length=10)),
                ('client_assignment', models.BooleanField(default=False)),
                ('assignment_file', models.FileField(upload_to=core.extra.upload_file)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='OtherProjectDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compensation_from_client', models.CharField(max_length=50)),
                ('travel_expense_reimbursement', models.CharField(max_length=50)),
                ('phone_reimbursement', models.CharField(max_length=50)),
                ('other_comments', models.TextField()),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deal_name', models.CharField(max_length=200)),
                ('zoho_id', models.CharField(max_length=100)),
                ('bd_email', models.EmailField(max_length=254)),
                ('company_name', models.CharField(max_length=100)),
                ('contact_name', models.CharField(max_length=100)),
                ('role_type', models.CharField(max_length=20)),
                ('model_type', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('flex_details', models.CharField(max_length=60)),
                ('stage', models.CharField(max_length=30)),
                ('status_description', models.TextField(blank=True)),
                ('next_step', models.TextField(blank=True)),
                ('post_status', models.CharField(blank=True, max_length=60)),
                ('project_created', models.BooleanField(default=False)),
                ('form_type', models.CharField(choices=[('general', 'general'), ('sales', 'sales'), ('content', 'content')], default='general', max_length=10)),
                ('status', models.IntegerField(choices=[(1, 'Project Proposal')], default=1)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('bd', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='admin_app.adminuser')),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.function')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.role')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Requirement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_positions', models.PositiveIntegerField(default=1)),
                ('min_total_experience_needed', models.IntegerField()),
                ('max_total_experience_needed', models.IntegerField()),
                ('min_relevant_experience', models.IntegerField(blank=True)),
                ('max_relevant_experience', models.IntegerField(blank=True)),
                ('educational_constraints', models.BooleanField(default=False)),
                ('education', models.CharField(max_length=100)),
                ('sale_type', models.CharField(blank=True, max_length=100)),
                ('describe_more', models.TextField(blank=True)),
                ('lead_generation_requirement', models.CharField(blank=True, max_length=100)),
                ('own_contact_required', models.CharField(blank=True, max_length=50)),
                ('if_yes', models.CharField(blank=True, max_length=100)),
                ('lead_expresses_interest', models.TextField(blank=True)),
                ('language', models.CharField(blank=True, max_length=20)),
                ('communication_skill_level', models.CharField(blank=True, max_length=50)),
                ('goals', models.TextField(blank=True)),
                ('content_type', models.CharField(blank=True, max_length=100)),
                ('quantum_min', models.PositiveIntegerField(blank=True)),
                ('quantum_max', models.PositiveIntegerField(blank=True)),
                ('quantum_unit', models.CharField(blank=True, max_length=20)),
                ('word_min', models.PositiveIntegerField(blank=True)),
                ('word_max', models.PositiveIntegerField(blank=True)),
                ('word_unit', models.CharField(blank=True, max_length=20)),
                ('sample_work', models.CharField(blank=True, max_length=20)),
                ('sample_work_detail', models.CharField(blank=True, max_length=200)),
                ('budget', models.PositiveIntegerField(blank=True)),
                ('content_duration_min', models.PositiveIntegerField(blank=True)),
                ('content_duration_max', models.PositiveIntegerField(blank=True)),
                ('content_duration_unit', models.PositiveIntegerField(blank=True)),
                ('target_audience', models.CharField(blank=True, max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('must_have_domains', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='must_have_domains', to='admin_app.domain')),
                ('must_have_skills', models.ManyToManyField(related_name='must_have_skills', to='admin_app.Skill')),
                ('nice_to_have_domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.domain')),
                ('nice_to_have_skills', models.ManyToManyField(blank=True, to='admin_app.Skill')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.DeleteModel(
            name='CRMData',
        ),
        migrations.AddField(
            model_name='otherprojectdetail',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project'),
        ),
        migrations.AddField(
            model_name='flexidetails',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project'),
        ),
        migrations.AddField(
            model_name='clientdetail',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project'),
        ),
    ]
