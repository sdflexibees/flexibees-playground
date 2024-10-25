# Generated by Django 3.1.4 on 2024-06-11 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admin_app', '0025_auto_20231009_1217'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('1', 'pending'), ('2', 'approved'), ('3', 'rejected')], default='1', max_length=5)),
                ('action_date', models.DateTimeField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'custom_roles',
            },
        ),
        migrations.CreateModel(
            name='CustomSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_name', models.CharField(max_length=150)),
                ('status', models.CharField(choices=[('1', 'pending'), ('2', 'approved'), ('3', 'rejected')], default='1', max_length=5)),
                ('action_date', models.DateTimeField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'custom_skills',
            },
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('1', 'Employer Created'), ('2', 'Profile Related'), ('3', 'Created Job'), ('4', 'Selection in Progress'), ('5', 'Job in Progress'), ('6', 'Completed')], default='1', max_length=5)),
                ('additional_info', models.JSONField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'employers',
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[('1', 'Created'), ('2', 'Published'), ('3', 'Interview Progress'), ('4', 'Candidate Selected'), ('5', 'Deal in Progress'), ('6', 'Completed')], default='1', max_length=5)),
                ('description', models.TextField()),
                ('details', models.JSONField(default={})),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.employer')),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.function')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='admin_app.role')),
                ('skills', models.ManyToManyField(related_name='job_skills', to='admin_app.Skill')),
            ],
            options={
                'db_table': 'jobs',
            },
        ),
        migrations.CreateModel(
            name='RoleMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='admin_app.function')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='admin_app.role')),
            ],
            options={
                'db_table': 'employer_role_mappings',
            },
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'user_types',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('user_type', models.CharField(choices=[('1', 'Employer')], default='1', max_length=2)),
                ('profile_image', models.URLField()),
                ('country_code', models.CharField(default='91', max_length=5)),
                ('mobile', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=200, null=True)),
                ('password', models.TextField()),
                ('otp', models.TextField(blank=True, null=True)),
                ('phone_verified', models.BooleanField(default=False)),
                ('email_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.usertype')),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='SkillMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role_mapping', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.rolemapping')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='admin_app.skill')),
            ],
            options={
                'db_table': 'skill_mappings',
            },
        ),
        migrations.CreateModel(
            name='JobCustomRoleSkills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('1', 'pending'), ('2', 'approved'), ('3', 'rejected')], default='1', max_length=5)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.job')),
                ('role', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='employer.customrole')),
                ('skill', models.ManyToManyField(to='employer.CustomSkill')),
            ],
            options={
                'db_table': 'job_custom_role_skills',
            },
        ),
        migrations.AddField(
            model_name='employer',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='employer.users'),
        ),
        migrations.CreateModel(
            name='DraftJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('1', 'Pending'), ('2', 'Published')], default='1', max_length=2)),
                ('details', models.JSONField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.employer')),
            ],
            options={
                'db_table': 'draft_jobs',
            },
        ),
        migrations.AddField(
            model_name='customskill',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.employer'),
        ),
        migrations.AddField(
            model_name='customrole',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.employer'),
        ),
        migrations.AddField(
            model_name='customrole',
            name='function',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='admin_app.function'),
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('website', models.URLField()),
                ('logo', models.URLField(null=True)),
                ('description', models.TextField()),
                ('size', models.CharField(choices=[('1', '1 to 10'), ('2', '11 to 50'), ('3', '51 to 400'), ('4', '401 to 1000'), ('5', 'above 1000')], max_length=5)),
                ('target_audience', models.CharField(choices=[('1', 'B2B'), ('2', 'B2C'), ('3', 'others')], max_length=5)),
                ('source', models.CharField(choices=[('1', 'Social media'), ('2', 'Referral'), ('3', 'Search engines'), ('4', 'others')], max_length=5)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.employer')),
                ('industry_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='admin_app.domain')),
            ],
            options={
                'db_table': 'companies',
            },
        ),
        migrations.AddIndex(
            model_name='customskill',
            index=models.Index(fields=['skill_name'], name='idx_custom_skill_name'),
        ),
        migrations.AddIndex(
            model_name='customrole',
            index=models.Index(fields=['role_name'], name='idx_custom_role_name'),
        ),
    ]
