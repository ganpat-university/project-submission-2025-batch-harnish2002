# Generated by Django 4.2.18 on 2025-03-10 18:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0039_alter_material_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='content',
        ),
    ]
