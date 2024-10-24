# Generated by Django 3.1.4 on 2021-01-08 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0006_configuration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='configuration',
            name='tag_name',
        ),
        migrations.AddField(
            model_name='configuration',
            name='tags',
            field=models.ManyToManyField(to='admin_app.Tags'),
        ),
    ]
