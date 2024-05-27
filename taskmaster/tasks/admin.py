from django.contrib import admin
from .models import CustomUser, Project, ProjectRole, Task, Notification
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'role', 'date_registered', 'last_login']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(ProjectRole)
admin.site.register(Task)
admin.site.register(Notification)