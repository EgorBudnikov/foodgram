"""Имя приложение и отображение в админ-панели."""
from django.apps import AppConfig


class RecipeConfig(AppConfig):
    """Наименование приложения в админ-панели."""

    name = 'recipe'
    verbose_name = 'Рецепты'
