# Generated by Django 5.0.4 on 2024-05-24 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_alter_customuser_notification_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='notification_settings',
            field=models.JSONField(default=dict),
        ),
    ]
