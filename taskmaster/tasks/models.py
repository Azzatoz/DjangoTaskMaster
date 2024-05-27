from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class CustomUser(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(blank=False, unique=True)
    role = models.CharField(max_length=50)
    date_registered = models.DateTimeField(auto_now_add=True)
    login_at = models.DateTimeField(auto_now=True)
    notification_settings = models.JSONField(default=dict, blank=False)

    def save(self, *args, **kwargs):
        # При создании нового пользователя заполняем все настройки уведомлений
        if not self.pk:  # Проверяем, что это новый пользователь
            self.notification_settings = {notification_type[0]: True for notification_type in Notification.NOTIFICATION_TYPES}
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    owner = models.ForeignKey(CustomUser, related_name='owned_projects', on_delete=models.CASCADE)
    users = models.ManyToManyField(get_user_model(), through='ProjectRole')

    def __str__(self):
        return self.name


class ProjectRole(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Владелец'),
        ('moderator', 'Модератор'),
        ('executor', 'Исполнитель')
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='executor')

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} в проекте {self.project.name}"


class Task(models.Model):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    PRIORITY_CHOICES = [
        (LOW, 'Низкий'),
        (MEDIUM, 'Средний'),
        (HIGH, 'Высокий'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=LOW)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_tasks')
    created_by = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE, related_name='created_tasks')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('added_to_project', 'Вас добавили в проект'),
        ('edited_project', 'Проект был обновлен'),
        ('project_completed', 'Проект был выполнен'),
        ('project_reopened', 'Проект снова открыт'),
        ('removed_from_project', 'Вас выгнали из проекта'),
        ('task_assigned', 'Для вас назначили задачу'),
        ('task_edited', 'Задача обновлена'),
        ('task_deleted', 'Задача удалена'),
        ('task_completed', 'Задача была выполнена'),
        ('task_reopened', 'Задача снова открыта'),
        ('task_due_today', 'Сегодня нужно выполнить задачу'),
        ('task_overdue', 'Вы просрочили задачу'),
        ('project_role', 'Вас назначили на новую роль'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}"

    def get_absolute_url(self):
        if self.task:
            return reverse('project_detail', args=[self.task.id])
        elif self.project:
            return reverse('project_detail', args=[self.project.id])
        return '#'
