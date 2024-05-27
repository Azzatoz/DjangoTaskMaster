# Generated by Django 5.0.4 on 2024-05-23 09:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('added_to_project', 'Вас добавили в проект'), ('edited_project', 'Проект был обновлен'), ('project_completed', 'Проект был выполнен'), ('project_reopened', 'Проект снова открыт'), ('removed_from_project', 'Вас выгнали из проекта'), ('task_assigned', 'Для вас назначили задачу'), ('task_edited', 'Задача обновлена'), ('task_deleted', 'Задача удалена'), ('task_completed', 'Задача была выполнена'), ('task_reopened', 'Задача снова открыта'), ('task_due_today', 'Сегодня нужно выполнить задачу'), ('task_overdue', 'Вы просрочили задачу'), ('project_role', 'Вас назначили на новую роль')], max_length=50)),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.project')),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]