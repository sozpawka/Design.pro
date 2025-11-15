from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
import re

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Повтор пароля')
    agree = forms.BooleanField(label='Согласие на обработку персональных данных')

    class Meta:
        model = User
        fields = ('username','first_name','email')

    def clean_first_name(self):
        v = self.cleaned_data.get('first_name','')
        if not re.fullmatch(r'[А-Яа-яЁё\-\s]+', v):
            raise ValidationError('ФИО должно содержать только кириллицу, пробелы и дефис.')
        return v

    def clean_username(self):
        v = self.cleaned_data.get('username','')
        if not re.fullmatch(r'[A-Za-z\-]+', v):
            raise ValidationError('Логин — только латиница и дефис.')
        if User.objects.filter(username=v).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return v

    def clean_email(self):
        v = self.cleaned_data.get('email','')
        # let Django's EmailField handle format at field level; here ensure presence
        if not v:
            raise ValidationError('Укажите email.')
        return v

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError({'password2':'Пароли не совпадают.'})
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class ApplicationForm(forms.ModelForm):
    class Meta:
        from .models import Application
        model = Application
        fields = ('title','category','image','description')
