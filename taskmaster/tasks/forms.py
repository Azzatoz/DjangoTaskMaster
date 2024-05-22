from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Project, Task


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')


class SignInForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'assigned_to']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(projects=project)
            self.fields['assigned_to'].label_from_instance = lambda obj: f'{obj.username}'


class TaskFilterForm(forms.Form):
    search = forms.CharField(required=False, label='Название задачи')
    status = forms.ChoiceField(required=False, choices=[('', 'Любой'), ('completed', 'Завершенные'), ('not_completed', 'Не завершенные')], label='Статус')
    priority = forms.ChoiceField(required=False, choices=[('', 'Любой'), (1, 'Низкий'), (2, 'Средний'), (3, 'Высокий')], label='Приоритет')
    due_date_from = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}), label='Срок выполнения (с)')
    due_date_to = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}), label='Срок выполнения (по)')
