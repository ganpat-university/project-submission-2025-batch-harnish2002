# Generated by Django 4.2.18 on 2025-03-01 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgs', '0025_passwordresetrequest'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PasswordResetRequest',
        ),
    ]
