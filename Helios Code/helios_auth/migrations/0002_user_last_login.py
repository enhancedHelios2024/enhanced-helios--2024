# Generated by Django 2.2.4 on 2024-01-28 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helios_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
