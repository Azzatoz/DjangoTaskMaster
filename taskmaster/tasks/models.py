from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
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
    users = models.ManyToManyField(get_user_model(), related_name='projects')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_projects')

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=0)
    # status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE, related_name='created_tasks')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
