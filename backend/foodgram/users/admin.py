"""Регистрация модели в админ-панели."""
from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки модели в админке."""

    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')
