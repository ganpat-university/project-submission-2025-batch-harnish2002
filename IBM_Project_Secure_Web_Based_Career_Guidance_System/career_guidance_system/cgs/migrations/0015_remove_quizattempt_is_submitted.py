# Generated by Django 4.2.18 on 2025-02-12 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0014_quizattempt_is_submitted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizattempt',
            name='is_submitted',
        ),
    ]
