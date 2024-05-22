from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(blank=False, unique=True)
    role = models.CharField(max_length=50)
    date_registered = models.DateTimeField(auto_now_add=True)
    login_at = models.DateTimeField(auto_now=True)

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
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE, related_name='created_tasks')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
