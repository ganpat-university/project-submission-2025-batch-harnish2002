# Generated by Django 4.2.18 on 2025-03-10 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0038_alter_material_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='content',
            field=models.TextField(help_text='Enter text content if Text Material or upload a video file path if Video Material'),
        ),
    ]
