from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, ApplicationForm
from .models import Application

def index(request):
    recent_done = Application.objects.filter(status='done').order_by('-created')[:4]
    in_progress_count = Application.objects.filter(status='in_progress').count()
    return render(request, 'studio/index.html', {'recent_done': recent_done, 'in_progress_count': in_progress_count})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна. Войдите.')
            return redirect('studio:login')
    else:
        form = RegistrationForm()
    return render(request, 'studio/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('studio:dashboard')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'studio/login.html')

def user_logout(request):
    logout(request)
    return redirect('studio:index')

@login_required
def dashboard(request):
    apps = request.user.applications.all()
    return render(request, 'studio/dashboard.html', {'applications': apps})

@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user  # связываем заявку с пользователем
            app.save()
            messages.success(request, 'Заявка создана.')
            return redirect('studio:dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'studio/application_form.html', {'form': form})

@login_required
def delete_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        app.delete()
        messages.success(request, 'Заявка удалена.')
        return redirect('studio:dashboard')
    return render(request, 'studio/application_confirm_delete.html', {'application': app})

@login_required
def application_detail(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    return render(request, 'studio/application_detail.html', {'application': app})

@login_required
def edit_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка обновлена.')
            return redirect('studio:application_detail', pk=app.pk)
    else:
        form = ApplicationForm(instance=app)
    return render(request, 'studio/application_form.html', {'form': form, 'edit': True})