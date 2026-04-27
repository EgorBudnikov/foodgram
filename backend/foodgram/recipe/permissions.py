"""Модуль с правами доступа для рецептов.

Содержит класс Permission для проверки доступа пользователей
к просмотру, созданию, редактированию и удалению рецептов.
"""

from rest_framework import permissions


class UserRecipePermissions(permissions.BasePermission):
    """Пермишн на проверку доступа к рецептам."""

    def has_permission(self, request, view):
        """Проверка доступа на уровне запроса.

        Разрешает безопасные методы (GET, HEAD, OPTIONS) всем пользователям.
        Для остальных методов требуется аутентификация.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверка доступа на уровне объекта.

        Разрешает безопасные методы всем.
        Для редактирования и удаления требуется, чтобы пользователь
        был автором рецепта.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
