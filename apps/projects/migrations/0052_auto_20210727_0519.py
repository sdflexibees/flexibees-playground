# Generated by Django 3.1.4 on 2021-07-27 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0022_auto_20210708_0806'),
        ('projects', '0051_auto_20210520_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='admin_app.role'),
        ),
    ]
