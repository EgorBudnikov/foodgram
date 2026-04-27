"""Сериализаторы для работы с рецептами, тегами и ингредиентами.

Содержит сериализаторы для:
- тегов и ингредиентов
- создания, обновления, получения рецептов
- короткого представления рецептов
- валидации ингредиентов и тегов
"""

import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipe.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения тегов."""

    class Meta:
        """Мета-класс для TagsSerializer."""

        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для получения ингредиентов."""

    class Meta:
        """Мета-класс для IngredientSerializer."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Серилизатор для получения рецептов в короткой форме."""

    image = serializers.SerializerMethodField()

    class Meta:
        """Мета-класс для RecipeShortSerializer."""

        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        """Возвращает абсолютный URL изображения рецепта."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class RecipeIngredientsSerializer(serializers.Serializer):
    """Сериализатор для связных ингредиентов с рецептами."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)


class RecipeSerializer(serializers.ModelSerializer):
    """Серилизатор для создания и обновления рецептов."""

    image = serializers.CharField(write_only=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    ingredients = RecipeIngredientsSerializer(many=True, write_only=True)

    class Meta:
        """Мета-класс для RecipeSerializer."""

        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'tags', 'cooking_time'
        )
        read_only_fields = ['id', 'author']

    def update(self, instance, validated_data):
        """Обновление рецепта с изображением, тегов и ингредиентами."""
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        fields = (
            'name', 'text',
            'ingredients', 'tags', 'cooking_time'
        )
        fields_request = self.context['request'].data.keys()

        for field in fields:
            if field not in fields_request:
                raise serializers.ValidationError(
                    f'Нет обязательного поля {field}'
                )

        if 'image' in validated_data:
            img_data = validated_data.pop('image')
            fmt, img = img_data.split(';base64,')
            ext = fmt.split('/')[-1]
            file_data = base64.b64decode(img)
            instance.image.save(
                f'recipe_{instance.id}.{ext}',
                ContentFile(file_data),
                save=False
            )

        instance.save()

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            tags = self.validate_tags(tags_data)
            instance.tags.set(tags)
        else:
            raise serializers.ValidationError(
                'Поле tags обязательно к заполнению.'
            )

        if 'ingredients' in validated_data:
            ing_data = validated_data.pop('ingredients')
            ing = self.validate_ingredients(ing_data)
            instance.recipe_ingredients.all().delete()

            for item in ing:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient_id=item.get('id'),
                    amount=item.get('amount')
                )
        else:
            raise serializers.ValidationError(
                'Поле ingredients обязательно к заполнению.'
            )
        return instance

    def validate_tags(self, value):
        """Проверка тегов: наличие, существование в БД, дубликаты."""
        if not value:
            raise serializers.ValidationError(
                'Поле tags должно быть заполнено.'
            )

        tag_ids = []

        for tag_id in value:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f'Тег с id={tag_id} не найден.'
                )

            if tag_id in tag_ids:
                raise serializers.ValidationError(
                    f'Тег с id={tag_id} уже добавлен.'
                )
            tag_ids.append(tag_id)

        return tag_ids

    def validate_ingredients(self, value):
        """Проверка ингредиентов: наличие, существование, дубликаты, кол-во."""
        if not value:
            raise serializers.ValidationError(
                'Поле ингредиенты должно быть заполнено.'
            )

        ingredient_ids = set()

        for ing in value:
            ingredient_id = ing.get('id')

            if not ingredient_id:
                raise serializers.ValidationError(
                    'У каждого ингредиента должен быть указан id.'
                )

            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиент с id={ingredient_id} не найден.'
                )
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    f'Такой ингредиент с id={ingredient_id} уже добавлен.'
                )
            ingredient_ids.add(ingredient_id)

            if ing.get('amount', 0) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )

        return value

    def create(self, validated_data):
        """Создание рецепта с обработкой изображения, тегов и ингредиентов."""
        img_data = validated_data.pop('image')
        tags = validated_data.pop('tags')
        tags = self.validate_tags(tags)
        ingredients = validated_data.pop('ingredients')
        ingredients = self.validate_ingredients(ingredients)

        fmt, img = img_data.split(';base64,')
        ext = fmt.split('/')[-1]
        img_data = base64.b64decode(img)

        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data
        )

        recipe.image.save(
            f'recipe_{recipe.id}.{ext}',
            ContentFile(img_data),
            save=True
        )

        recipe.tags.set(tags)

        for item in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=item.get('id'),
                amount=item.get('amount')
            )

        return recipe


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для получения конкретных рецептов."""

    tags = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        """Мета-класс для RecipeDetailSerializer."""

        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'text', 'cooking_time'
        ]

    def get_author(self, obj):
        """Возвращает данные автора рецепта."""
        from users.serializers import UserDetailSerializer
        request = self.context.get('request')

        return UserDetailSerializer(
            obj.author, context={'request': request}
        ).data

    def get_tags(self, obj):
        """Возвращает список тегов рецепта."""
        return [
            {
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug
            }
            for tag in obj.tags.all()
        ]

    def get_ingredients(self, obj):
        """Возвращает список ингредиентов рецепта с количеством."""
        ingreds = obj.recipe_ingredients.all().select_related('ingredient')
        return [
            {
                'id': ing.ingredient.id,
                'name': ing.ingredient.name,
                'measurement_unit': ing.ingredient.measurement_unit,
                'amount': ing.amount
            }
            for ing in ingreds
        ]

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное текущим пользователем."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в корзину текущим пользователем."""
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_image(self, obj):
        """Возвращает абсолютный URL изображения рецепта."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
