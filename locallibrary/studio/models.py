from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CATEGORY_CHOICES = [
    ('design', 'Дизайн'),
    ('development', 'Разработка'),
    ('marketing', 'Маркетинг'),
]

STATUS_CHOICES = [
    ('new', 'Новая'),
    ('in_progress', 'В работе'),
    ('done', 'Выполнена'),
]

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='applications/', blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"
