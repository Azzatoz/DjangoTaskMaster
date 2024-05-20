from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, SignInForm, ProjectForm, TaskForm


def home(request):
    projects = Project.objects.filter(email=request.user)
    tasks = Task.objects.filter(project__email=request.user, status='pending').order_by('priority')
    return render(request, 'home.html', {'projects': projects, 'tasks': tasks})


def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.email = request.user
            project.save()
            return redirect('home')
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})

def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('home')
    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form})


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
                # Обработка случая, когда пользователь не найден или пароль неверен
                # Можно добавить соответствующее сообщение об ошибке
                pass
    else:
        form = SignInForm()
    return render(request, 'signin.html', {'form': form})
