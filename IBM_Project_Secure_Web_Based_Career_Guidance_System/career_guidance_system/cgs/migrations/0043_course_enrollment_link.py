# Generated by Django 4.2.18 on 2025-03-14 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0042_alter_material_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='enrollment_link',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
