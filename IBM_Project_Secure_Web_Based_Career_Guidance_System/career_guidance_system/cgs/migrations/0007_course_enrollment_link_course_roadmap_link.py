# Generated by Django 4.2.18 on 2025-02-10 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0006_course_enrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='enrollment_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='course',
            name='roadmap_link',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
