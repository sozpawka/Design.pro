from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.db.models import Count

from .forms import (
    RegistrationForm,
    ApplicationForm,
    ApplicationStatusDoneForm,
    ApplicationStatusInProgressForm,
)
from .models import Application, Category


# Проверка прав администратора
def is_admin(user):
    return user.is_active and (user.is_staff or user.is_superuser)


# Главная страница
def index(request):
    recent_done = Application.objects.filter(status=Application.STATUS_DONE).order_by('-created')[:4]
    in_progress_count = Application.objects.filter(status=Application.STATUS_IN_PROGRESS).count()
    return render(request, 'studio/index.html', {
        'recent_done': recent_done,
        'in_progress_count': in_progress_count
    })


# Регистрация
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно. Войдите в систему.")
            return redirect('studio:login')
    else:
        form = RegistrationForm()
    return render(request, 'studio/register.html', {'form': form})


# Авторизация
def login_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        pwd = request.POST.get('password')

        user = authenticate(request, username=uname, password=pwd)
        if user:
            login(request, user)
            messages.success(request, "Успешный вход")
            return redirect('studio:dashboard')
        else:
            messages.error(request, "Неверный логин или пароль")

    return render(request, 'studio/login.html')


# Выход
@login_required
def logout_view(request):
    logout(request)
    return redirect('studio:index')


# Личный кабинет
@login_required
def dashboard(request):
    qs = Application.objects.filter(user=request.user)

    status = request.GET.get('status')
    if status in [Application.STATUS_NEW, Application.STATUS_IN_PROGRESS, Application.STATUS_DONE]:
        qs = qs.filter(status=status)

    applications = qs.order_by('-created')
    categories = Category.objects.all()

    return render(request, 'studio/dashboard.html', {
        'applications': applications,
        'categories': categories,
        'selected_status': status
    })


# Создание заявки
@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.status = Application.STATUS_NEW
            app.save()
            messages.success(request, "Заявка успешно создана")
            return redirect('studio:dashboard')
    else:
        form = ApplicationForm()

    return render(request, 'studio/application_form.html', {'form': form, 'edit': False})


# Детали заявки
@login_required
def application_detail(request, pk):
    app = get_object_or_404(Application, pk=pk)

    if not (request.user == app.user or is_admin(request.user)):
        return HttpResponseForbidden("Нет доступа к этой заявке")

    return render(request, 'studio/application_detail.html', {'application': app})


# Редактирование заявки
@login_required
def edit_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)

    if app.status != Application.STATUS_NEW:
        messages.error(request, "Редактирование возможно только для заявок со статусом 'Новая'")
        return redirect('studio:dashboard')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, "Заявка обновлена.")
            return redirect('studio:application_detail', pk=app.pk)
    else:
        form = ApplicationForm(instance=app)

    return render(request, 'studio/application_form.html', {'form': form, 'edit': True})


# Удаление заявки
@login_required
def delete_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)

    if not app.can_user_delete():
        messages.error(request, "Удаление возможно только для заявок в статусе 'Новая'")
        return redirect('studio:dashboard')

    if request.method == 'POST':
        app.delete()
        messages.success(request, "Заявка удалена")
        return redirect('studio:dashboard')

    return render(request, 'studio/application_confirm_delete.html', {'application': app})


# Список категорий
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.annotate(app_count=Count('applications')).order_by('name')
    return render(request, 'studio/category_list.html', {'categories': categories})


# Создание категории
@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()

        if not name or not slug:
            messages.error(request, "Имя и slug обязательны.")
            return render(request, 'studio/category_form.html', {'category': None})

        if Category.objects.filter(slug=slug).exists():
            messages.error(request, "Категория с таким slug уже существует.")
            return render(request, 'studio/category_form.html', {'category': None})

        Category.objects.create(name=name, slug=slug)
        messages.success(request, "Категория успешно создана.")
        return redirect('studio:category_list')

    return render(request, 'studio/category_form.html', {'category': None})


# Редактирование категории
@user_passes_test(is_admin)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()

        if not name or not slug:
            messages.error(request, "Имя и slug обязательны.")
            return render(request, 'studio/category_form.html', {'category': category})

        if Category.objects.filter(slug=slug).exclude(pk=category.pk).exists():
            messages.error(request, "Категория с таким slug уже существует.")
            return render(request, 'studio/category_form.html', {'category': category})

        category.name = name
        category.slug = slug
        category.save()
        messages.success(request, "Категория успешно обновлена.")
        return redirect('studio:category_list')

    return render(request, 'studio/category_form.html', {'category': category})


# Удаление категории
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.applications.all().delete()
        category.delete()
        messages.success(request, "Категория и связанные заявки удалены.")
        return redirect('studio:category_list')

    return render(request, 'studio/category_confirm_delete.html', {'category': category})


# Взять заявку в работу
@user_passes_test(is_admin)
def change_status_in_progress(request, pk):
    app = get_object_or_404(Application, pk=pk)

    if app.status != Application.STATUS_NEW:
        messages.error(request, "В работу можно взять только заявку со статусом «Новая».")
        return redirect('studio:application_detail', pk=app.pk)

    if request.method == 'POST':
        form = ApplicationStatusInProgressForm(request.POST, instance=app)
        if form.is_valid():
            app.admin_comment = form.cleaned_data.get('admin_comment', '')
            app.status = Application.STATUS_IN_PROGRESS
            app.save()
            messages.success(request, "Статус изменён на 'Принято в работу'")
            return redirect('studio:application_detail', pk=pk)
    else:
        form = ApplicationStatusInProgressForm(instance=app)

    return render(request, 'studio/change_status_in_progress.html', {'form': form, 'application': app})


# Завершить заявку
@user_passes_test(is_admin)
def change_status_done(request, pk):
    app = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        form = ApplicationStatusDoneForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            design_image = form.cleaned_data.get('design_image')
            if design_image:
                app.design_image = design_image
            app.status = Application.STATUS_DONE
            app.save()
            messages.success(request, "Статус изменён на 'Выполнена'")
            return redirect('studio:application_detail', pk=pk)
    else:
        form = ApplicationStatusDoneForm(instance=app)

    return render(request, 'studio/change_status_done.html', {'form': form, 'application': app})


# Отчёт по заявкам
@user_passes_test(is_admin)
def report(request):
    qs = Application.objects.all().select_related('category', 'user').order_by('-created')

    # Фильтр по статусу
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)

    # Фильтр по категории
    category = request.GET.get('category')
    if category:
        qs = qs.filter(category__id=category)

    # ---- Фильтр по датам ----
    start = request.GET.get('start')
    end = request.GET.get('end')

    if start:
        start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
        qs = qs.filter(created__gte=start_dt)

    if end:
        end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d")) + timedelta(days=1)
        qs = qs.filter(created__lt=end_dt)

    categories = Category.objects.all()

    return render(request, 'studio/report.html', {
        'apps': qs,
        'categories': categories,
        'start': start,
        'end': end
    })


# Панель администратора
@user_passes_test(is_admin)
def admin_panel(request):
    applications = Application.objects.all().select_related('category', 'user').order_by('-created')

    return render(request, 'studio/admin_panel.html', {
        'applications': applications,
        'total': applications.count(),
        'new_count': applications.filter(status=Application.STATUS_NEW).count(),
        'in_progress_count': applications.filter(status=Application.STATUS_IN_PROGRESS).count(),
        'done_count': applications.filter(status=Application.STATUS_DONE).count(),
    })
