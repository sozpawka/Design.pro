from django.contrib import admin
from .models import Application, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created')
    list_filter = ('status', 'category')
    search_fields = ('title', 'user__username', 'description')
