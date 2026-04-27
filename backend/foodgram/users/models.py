"""Модель пользователей.

- создана расширенная модель пользователя;
- указана дополнительные поля и проверки.
"""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя."""

    email = models.EmailField('E-mail', unique=True, max_length=254)
    avatar = models.ImageField(
        'Аватар', blank=True, null=True, upload_to='users/avatars')
    following = models.ManyToManyField(
        'self', symmetrical=False, blank=True,
        verbose_name='Подписки', related_name='followers')
    username = models.CharField(
        'Никнейм', max_length=150, unique=True,
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                message='В никнейме могут использоваться латинские буквы, .@-+'
            )])
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

    class Meta:
        """Оторажение в админ-панели."""

        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
