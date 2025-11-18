from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Application
import re

User = get_user_model()


# Форма регистрации пользователя
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Повтор пароля")
    agree = forms.BooleanField(label="Согласие на обработку персональных данных")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_first_name(self):
        v = self.cleaned_data.get("first_name", "").strip()
        if not re.match(r"^[А-Яа-яёЁ\s\-]+$", v):
            raise ValidationError("ФИО: только кириллица, пробел и дефис")
        return v

    def clean_last_name(self):
        v = self.cleaned_data.get("last_name", "").strip()
        if not re.match(r"^[А-Яа-яёЁ\s\-]+$", v):
            raise ValidationError("Фамилия: только кириллица, пробел и дефис")
        return v

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.match(r"^[A-Za-z0-9\-]+$", username):
            raise ValidationError("Логин: только латиница, цифры и дефис")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("Email обязателен")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password2"):
            self.add_error("password2", "Пароли не совпадают")
        if not cleaned.get("agree"):
            self.add_error("agree", "Необходимо согласие на обработку персональных данных")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# Форма создания/редактирования заявки
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("title", "category", "image", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_image(self):
        img = self.cleaned_data.get("image")
        if not img:
            raise ValidationError("Поле изображения обязательно")

        valid_types = ["image/jpeg", "image/png", "image/bmp"]
        if getattr(img, "content_type", None) not in valid_types:
            raise ValidationError("Допустимые форматы: jpg, jpeg, png, bmp")

        if img.size > 2 * 1024 * 1024:
            raise ValidationError("Максимальный размер изображения — 2 Мб")

        return img


# Статус: выполнена
class ApplicationStatusDoneForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("design_image",)

    def clean_design_image(self):
        img = self.cleaned_data.get("design_image")
        if not img:
            raise ValidationError("Необходимо загрузить изображение выполненного дизайна")

        valid_types = ["image/jpeg", "image/png", "image/bmp"]
        if getattr(img, "content_type", None) not in valid_types:
            raise ValidationError("Допустимые форматы: jpg, jpeg, png, bmp")

        if img.size > 2 * 1024 * 1024:
            raise ValidationError("Максимальный размер изображения — 2 Мб")

        return img


# Статус: принято в работу
class ApplicationStatusInProgressForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("admin_comment",)

    def clean_admin_comment(self):
        c = self.cleaned_data.get("admin_comment", "").strip()
        if not c:
            raise ValidationError("Комментарий обязателен")
        return c
