from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from .forms import SignUpForm, SignInForm, PasswordResetForm, ProjectForm, TaskForm, TaskFilterForm
from .models import Project, ProjectRole, Task, CustomUser, Notification
import json


@login_required
def show_notification_settings(request):
    user = request.user
    notification_settings = user.notification_settings
    notification_types = Notification.NOTIFICATION_TYPES
    return render(request, 'home.html', {
        'notification_settings': notification_settings,
        'notification_types': notification_types,
    })


@login_required
@require_POST
def save_notification_settings(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body.decode('utf-8'))
            selected_notifications = data.get('notification_type', [])
            request.user.notification_settings = {notif: (notif in selected_notifications) for notif, _ in Notification.NOTIFICATION_TYPES}
            request.user.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Это не AJAX-запрос'})


@login_required
@require_POST
def mark_all_notifications_as_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Пользователь не аутентифицирован'}, status=401)


@login_required
def home(request):
    user = request.user
    projects = Project.objects.filter(users=user)
    completed_projects = projects.filter(completed=True)
    incomplete_projects = projects.filter(completed=False)
    tasks = Task.objects.filter(due_date__range=[timezone.now().date(), timezone.now().date() + timedelta(days=3)])
    notifications = user.notifications.filter(read=False)
    notifications_count = notifications.count()

    # Получение настроек уведомлений и типов уведомлений
    notification_settings = user.notification_settings
    notification_types = Notification.NOTIFICATION_TYPES

    return render(request, 'home.html', {
        'completed_projects': completed_projects,
        'incomplete_projects': incomplete_projects,
        'tasks': tasks,
        'notifications': notifications,
        'notifications_count': notifications_count,
        'notification_settings': notification_settings,
        'notification_types': notification_types,
    })


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    roles = ProjectRole.objects.filter(project=project)
    form = TaskFilterForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data['search']:
            tasks = tasks.filter(title__icontains=form.cleaned_data['search'])

    return render(request, 'project_detail.html', {
        'project': project,
        'tasks': tasks,
        'roles': roles,
        'form': form,
    })


@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.users.add(request.user, through_defaults={'role': 'owner'})

            Notification.objects.create(
                user=request.user,
                notification_type='added_to_project',
                project=project
            )

            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Проверка, является ли пользователь владельцем проекта
    if project.owner != request.user:
        return HttpResponseForbidden("У вас нет прав на редактирование этого проекта.")

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            Notification.objects.create(
                user=request.user,
                notification_type='edited_project',
                project=project
            )
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'edit_project.html', {'form': form, 'project': project})


@login_required
def mark_project_completed(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Проверка, является ли пользователь владельцем проекта
    if project.owner != request.user:
        return HttpResponseForbidden("У вас нет прав на изменение статуса этого проекта.")

    project.completed = not project.completed
    project.save()

    # Обновление статусов задач проекта
    Task.objects.filter(project=project).update(completed=project.completed)

    # Определение типа уведомления в зависимости от статуса проекта
    notification_type = 'project_completed' if project.completed else 'project_reopened'

    # Создание уведомления для пользователя
    Notification.objects.create(
        user=request.user,
        notification_type=notification_type,
        project=project
    )

    return redirect('project_detail', project_id=project.id)


@login_required
def add_user_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Проверка прав доступа текущего пользователя
    user_role = ProjectRole.objects.filter(project=project, user=request.user).first()
    if not user_role or user_role.role not in ['owner', 'moderator']:
        return HttpResponseForbidden("У вас нет прав на добавление пользователей к этому проекту.")

    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'executor')
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            # Пользователь не найден, передаем сообщение об ошибке
            return render(request, 'project_detail.html', {
                'project': project,
                'error_message': f"Пользователь с именем {username} не найден."
            })

        ProjectRole.objects.get_or_create(project=project, user=user, defaults={'role': role})

        Notification.objects.create(
            user=user,
            notification_type='added_to_project',
            project=project
        )
        return redirect('project_detail', project_id=project.id)

    return redirect('project_detail', project_id=project.id)


@login_required
def remove_user_from_project(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)
    try:
        user = get_user_model().objects.get(id=user_id)
    except get_user_model().DoesNotExist:
        # Пользователь не найден, передаем сообщение об ошибке
        return render(request, 'project_detail.html', {
            'project': project,
            'error_message': f"Пользователь с ID {user_id} не найден."
        })

    role = ProjectRole.objects.filter(project=project, user=request.user).first()
    if not role or role.role == 'executor':
        return HttpResponseForbidden("У вас нет прав на удаление пользователей из проекта.")

    if project.owner == user:
        # Нельзя удалить владельца проекта
        return redirect('project_detail', project_id=project.id)

    ProjectRole.objects.filter(project=project, user=user).delete()

    Notification.objects.create(
        user=user,
        notification_type='removed_from_project',
        project=project
    )
    return redirect('project_detail', project_id=project.id)


@login_required
def add_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    role = ProjectRole.objects.filter(project=project, user=request.user).first()

    if not role or role.role == 'executor':
        return HttpResponseForbidden("У вас нет прав на добавление задач в этот проект.")

    if project.completed:
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            if not task.assigned_to:
                task.assigned_to = request.user
            task.completed = False
            task.created_by = request.user
            task.save()

            Notification.objects.create(
                user=task.assigned_to,
                notification_type='task_assigned',
                project=project,
                task=task
            )
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(project=project)
    return render(request, 'add_task.html', {'form': form, 'project': project})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    role = ProjectRole.objects.filter(project=task.project, user=request.user).first()

    if not role or role.role == 'executor':
        return HttpResponseForbidden("У вас нет прав на добавление задач в этот проект.")

    if project.completed:
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            if not task.assigned_to:
                task.assigned_to = request.user
            task.completed = False
            task.created_by = request.user
            task.save()

            Notification.objects.create(
                user=task.assigned_to,
                notification_type='task_assigned',
                project=project,
                task=task
            )
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form, 'project': project})


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Проверка роли текущего пользователя
    role = ProjectRole.objects.filter(project=task.project, user=request.user).first()
    if role and role.role == 'executor':
        return HttpResponseForbidden("У вас нет прав на удаление этой задачи.")

    project_id = task.project.id
    task.delete()

    Notification.objects.create(
        user=task.assigned_to,
        notification_type='task_deleted',
        project=task.project
    )

    return redirect('project_detail', project_id=project_id)


@login_required
def mark_task_completed(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.completed:
        task.completed = False
        notification_type = 'task_reopened'
    else:
        task.completed = True
        notification_type = 'task_completed'
    task.save()

    Notification.objects.create(
        user=task.assigned_to,
        notification_type=notification_type,
        project=task.project,
        task=task
    )

    return redirect('project_detail', project_id=task.project.id)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # Load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form = SignInForm()
            return render(request, 'signin.html', {'form': form})
    else:
        form = SignInForm()
    return render(request, 'signin.html', {'form': form})


def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']

            try:
                user = User.objects.get(username=username, email=email)
                user.password = make_password(new_password)
                user.save()
                return HttpResponse("Пароль успешно изменен.")
            except ObjectDoesNotExist:
                return HttpResponse("Пользователь с указанным именем пользователя и электронной почтой не найден.")
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password.html', {'form': form})