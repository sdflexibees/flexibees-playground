# Generated by Django 3.1.4 on 2023-08-28 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0057_auto_20230717_0358'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('previous_email', models.EmailField(max_length=254)),
                ('otp', models.TextField(blank=True)),
                ('verified', models.BooleanField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate')),
            ],
        ),
    ]