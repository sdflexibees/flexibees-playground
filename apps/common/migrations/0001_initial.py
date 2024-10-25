# Generated by Django 3.1.4 on 2024-06-24 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employer', '0001_initial'),
        ('admin_app', '0025_auto_20231009_1217'),
    ]

    operations = [
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
                'db_table': 'roles_mappings',
            },
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'types',
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
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.usertype')),
            ],
            options={
                'db_table': 'user_infos',
            },
        ),
        migrations.CreateModel(
            name='SkillMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role_mapping', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.rolemapping')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='admin_app.skill')),
            ],
            options={
                'db_table': 'skills_mappings',
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
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.employer')),
            ],
            options={
                'db_table': 'custom_skill_mappings',
            },
        ),
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
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employer.employer')),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='admin_app.function')),
            ],
            options={
                'db_table': 'custom_role_mappings',
            },
        ),
        migrations.AddIndex(
            model_name='customskill',
            index=models.Index(fields=['skill_name'], name='idx_custom_skill_names'),
        ),
        migrations.AddIndex(
            model_name='customrole',
            index=models.Index(fields=['role_name'], name='idx_custom_role_names'),
        ),
    ]
