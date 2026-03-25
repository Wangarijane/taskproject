from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Task
from .forms import TaskForm

def is_admin(user):
    """Check if user is admin/superuser"""
    return user.is_superuser or user.is_staff

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "tasks/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("task_list")
    else:
        form = AuthenticationForm()
    return render(request, "tasks/login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def task_list(request):
    # If user is admin, show ALL tasks
    if is_admin(request.user):
        tasks = Task.objects.all()
        is_admin_view = True
    else:
        # Regular user sees only their tasks
        tasks = Task.objects.filter(user=request.user)
        is_admin_view = False
        
    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'is_admin': is_admin_view
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_update(request, id):
    if is_admin(request.user):
        task = get_object_or_404(Task, id=id)
    else:
        task = get_object_or_404(Task, id=id, user=request.user)
        
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, id):
    if is_admin(request.user):
        task = get_object_or_404(Task, id=id)
    else:
        task = get_object_or_404(Task, id=id, user=request.user)
        
    task.delete()
    return redirect('task_list')