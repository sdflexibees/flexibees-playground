# Generated by Django 3.1.4 on 2021-01-05 12:55

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.TextField()),
                ('country_code', models.CharField(default='91', max_length=5)),
                ('phone', models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='Please Enter correct Contact no.', regex='^\\d{10,15}$')])),
                ('level', models.PositiveIntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Expert')])),
                ('roles', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=11), size=None)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('published', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]