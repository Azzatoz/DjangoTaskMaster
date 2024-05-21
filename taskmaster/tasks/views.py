from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, SignInForm, ProjectForm, TaskForm
from .models import Project, Task, CustomUser


@login_required
def home(request):
    projects = Project.objects.filter(users=request.user)
    completed_projects = projects.filter(completed=True)
    incomplete_projects = projects.filter(completed=False)
    return render(request, 'home.html', {
        'completed_projects': completed_projects,
        'incomplete_projects': incomplete_projects,
    })


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(project=project)
    return render(request, 'project_detail.html', {'form': form, 'project': project})


@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})


def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'edit_project.html', {'form': form, 'project': project})


@login_required
def mark_project_completed(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.completed = not project.completed
    project.save()
    if project.completed:
        Task.objects.filter(project=project).update(completed=True)
    else:
        Task.objects.filter(project=project).update(completed=False)

    return redirect('project_detail', project_id=project.id)


def add_user_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        user = get_object_or_404(CustomUser, username=username)
        project.users.add(user)
        return redirect('project_detail', project_id=project.id)
    return redirect('project_detail', project_id=project.id)


@login_required
def add_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.completed:
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.completed = True
            task.created_by = request.user
            task.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form, 'project': project})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=task.project.id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})


@login_required
def mark_task_completed(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = True
    task.save()
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
