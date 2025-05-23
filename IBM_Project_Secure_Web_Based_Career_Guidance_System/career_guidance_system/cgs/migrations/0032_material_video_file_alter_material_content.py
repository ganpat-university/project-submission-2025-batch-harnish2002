# Generated by Django 4.2.18 on 2025-03-10 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0031_remove_course_enrollment_link_delete_enrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='video_file',
            field=models.FileField(blank=True, help_text='Upload video file for video materials', null=True, upload_to='course_videos/'),
        ),
        migrations.AlterField(
            model_name='material',
            name='content',
            field=models.TextField(blank=True, help_text='Text content for text materials', null=True),
        ),
    ]
