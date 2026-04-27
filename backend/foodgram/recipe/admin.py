"""Настройка админ-панели для моделей приложения recipe.

Содержит классы администратора для моделей:
- Recipe: рецепты с поиском, фильтрацией и кастомным полем
- Ingredient: ингредиенты с поиском по названию
- Tag: теги с автозаполнением слага
- Favorite: избранное
- ShoppingCart: корзина покупок
- RecipeIngredient: связь рецептов с ингредиентами
- RecipeShortLink: короткие ссылки
"""

from django.contrib import admin

from recipe.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeShortLink,
    ShoppingCart,
    Tag,
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административная панель для модели Recipe."""

    list_display = ('author', 'name', 'favourite_count')
    search_fields = ('author__username', 'author__email', 'name')
    list_filter = ('tags',)

    @admin.display(description='Рецепт в избранном')
    def favourite_count(self, recipe: Recipe):
        """Возвращает количество добавлений рецепта в избранное."""
        return recipe.favorite_recipe.all().count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административная панель для модели Ingredient."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административная панель для модели Tag."""

    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Административная панель для модели Favorite."""

    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Административная панель для модели ShoppingCart."""

    list_display = ('user', 'recipe')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Административная панель для модели RecipeIngredient."""

    list_display = ('ingredient', 'recipe', 'amount')


@admin.register(RecipeShortLink)
class RecipeShortLinkAdmin(admin.ModelAdmin):
    """Административная панель для модели RecipeShortLink."""

    list_display = ('code', 'recipe', 'date')
