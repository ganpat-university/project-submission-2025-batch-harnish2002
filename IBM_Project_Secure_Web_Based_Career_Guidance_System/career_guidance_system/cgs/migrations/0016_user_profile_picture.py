# Generated by Django 4.2.18 on 2025-02-13 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0015_remove_quizattempt_is_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
