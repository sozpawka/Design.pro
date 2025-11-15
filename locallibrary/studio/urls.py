from django.urls import path
from . import views

app_name = 'studio'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('application/create/', views.create_application, name='create_application'),
    path('application/<int:pk>/delete/', views.delete_application, name='delete_application'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/edit/', views.edit_application, name='edit_application'),

]
