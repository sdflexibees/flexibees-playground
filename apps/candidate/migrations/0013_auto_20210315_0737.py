# Generated by Django 3.1.4 on 2021-03-15 07:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0019_adminuser_active_projects'),
        ('projects', '0046_auto_20210312_0913'),
        ('candidate', '0012_auto_20210315_0454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentfeedback',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='clientfeedback',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='flexifitfeedback',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='functionalfeedback',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='SelfAssessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.skill')),
            ],
        ),
    ]