# Generated by Django 3.1.4 on 2021-04-08 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0025_remove_employmentdetail_industry_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='hear_about_flexibees',
            field=models.CharField(choices=[('others', 'Others'), ('facebook', 'Facebook'), ('instagram', 'Instagram'), ('linkedin', 'LinkedIn'), ('twitter', 'Twitter'), ('whatsapp', 'WhatsApp'), ('referral_scheme', 'Referral Scheme'), ('other_website_or_women_group', 'Other website or Women group'), ('google_search', 'Google search'), ('news_or_media', 'News or Media'), ('word_of_mouth', 'Word of mouth')], max_length=50),
        ),
    ]