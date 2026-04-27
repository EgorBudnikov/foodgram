"""Имя приложение и отображение в админ-панели."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Наименвоание приложения."""

    name = 'users'
    verbose_name = 'Пользователи'
