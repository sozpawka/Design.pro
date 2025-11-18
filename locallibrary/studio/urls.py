from django.urls import path
from . import views

app_name = 'studio'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('application/create/', views.create_application, name='create_application'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/edit/', views.edit_application, name='edit_application'),
    path('application/<int:pk>/delete/', views.delete_application, name='delete_application'),

    path('admin-panel/', views.admin_panel, name='admin_panel'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('application/<int:pk>/in_progress/', views.change_status_in_progress, name='change_status_in_progress'),
    path('application/<int:pk>/done/', views.change_status_done, name='change_status_done'),

]
