# Generated by Django 5.0.4 on 2024-05-24 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='notification_setting',
            field=models.JSONField(default=dict),
        ),
    ]