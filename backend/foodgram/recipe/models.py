"""Модели для работы с рецептами, тегами, ингредиентами.

Содержит модели:
- Recipe: основной модель рецепта
- Tag: теги для категоризации рецептов
- Ingredient: ингредиенты
- RecipeIngredient: связующая модель рецепта и ингредиентов с количеством
- Favorite: избранные рецепты пользователя
- ShoppingCart: список покупок пользователя
- RecipeShortLink: короткие ссылки на рецепты
"""

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Картинка', upload_to='recipe/recipes')
    text = models.TextField('Текстовое описание')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='ингредиенты'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        help_text='Время приготовления в минутах.',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        """Мета-класс для модели Recipe."""

        ordering = ['-id']
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        """Строковое представление рецепта."""
        return self.name


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-класс для модели Favorite."""

        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    """Модель корзины."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-класс для модели ShoppingCart."""

        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            )
        ]


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField('Название', unique=True, max_length=32)
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=32,
        null=True,
        blank=True,
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            message='В слаге могут быть латинские буквы, цифры, - и _.'
        )],
        help_text='Если слага нет, то он будет сформирован автоматически.'
    )

    def save(self, *args, **kwargs):
        """Автоматическая генерация слага при сохранении."""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)[:32]

            counter = 1
            original_slug = self.slug
            while Tag.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug[:29]}-{counter}'
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        """Строковое представление тега."""
        return self.name

    class Meta:
        """Мета-класс для модели Tag."""

        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        default_related_name = 'tags'


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        """Мета-класс для модели Ingredient."""

        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        default_related_name = 'ingredients'

    def __str__(self):
        """Строковое представление ингредиента."""
        return self.name


class RecipeIngredient(models.Model):
    """Связующая модель рецепта и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        """Мета-класс для модели RecipeIngredient."""

        default_related_name = 'recipe_ingredients'
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        """Строковое представление ингредиента в рецепте."""
        return (
            f'{self.ingredient.name}:{self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class RecipeShortLink(models.Model):
    """Модель для хранения коротких ссылок рецептов."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    code = models.CharField('Код', max_length=50, unique=True)
    date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        """Мета-класс для модели RecipeShortLink."""

        default_related_name = 'recipe_short'
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
