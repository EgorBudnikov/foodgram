"""Вьюхи для работы с рецептами, тегами и ингредиентами.

Содержит ViewSet для:
- чтения тегов и ингредиентов
- создания, обновления, удаления рецептов
- добавления/удаления рецептов в избранное и корзину
- генерации коротких ссылок
- скачивания списка покупок
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (Favorite, Ingredient, Recipe, RecipeShortLink,
                           ShoppingCart, Tag)
from recipe.permissions import UserRecipePermissions
from recipe.serializers import (IngredientSerializer, RecipeDetailSerializer,
                                RecipeSerializer, RecipeShortSerializer,
                                TagsSerializer)
from recipe.utils import generate_short_code
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для чтения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для чтения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Фильтрация ингредиентов по названию (регистронезависимо)."""
        queryset = super().get_queryset()

        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки рецептов."""

    filter_backends = [DjangoFilterBackend]
    permission_classes = [UserRecipePermissions]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ('create', 'partial_update'):
            return RecipeSerializer
        return RecipeDetailSerializer

    def get_queryset(self):
        """Фильтрация рецептов по тегам, автору, избранному и корзине."""
        queryset = Recipe.objects.all().order_by('-id').prefetch_related(
            'tags',
            'recipe_ingredients__ingredient'
        )
        user = self.request.user

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        is_favorite = self.request.query_params.get('is_favorited')
        if is_favorite == '1' and user.is_authenticated:
            queryset = queryset.filter(favorite_recipe__user=user)

        is_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_shopping_cart == '1' and user.is_authenticated:
            queryset = queryset.filter(in_shopping_cart__user=user)

        return queryset

    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление рецепта с возвратом полных данных."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        detail_serializer = RecipeDetailSerializer(
            instance, context={'request': request}
        )
        return Response(detail_serializer.data)

    def create(self, request, *args, **kwargs):
        """Создание рецепта с возвратом полных данных."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        detail_serializer = RecipeDetailSerializer(
            serializer.instance, context={'request': request}
        )
        return Response(detail_serializer.data, status=201)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Генерация короткой ссылки на рецепт."""
        recipe = self.get_object()

        short_link_obj = RecipeShortLink.objects.filter(recipe=recipe).first()

        if short_link_obj:
            code = short_link_obj.code
        else:
            code = generate_short_code()
            while RecipeShortLink.objects.filter(code=code).exists():
                code = generate_short_code()
            RecipeShortLink.objects.create(recipe=recipe, code=code)

        short_link = request.build_absolute_uri(f'/s/{code}')
        return Response({'short-link': short_link}, status=200)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного."""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            is_favorite = Favorite.objects.filter(
                user=user, recipe=recipe
            ).exists()

            if is_favorite:
                return Response(
                    {'error': 'Рецепт уже добавлен в избранное.'},
                    status=400
                )
            else:
                Favorite.objects.create(user=user, recipe=recipe)
                serializer = RecipeShortSerializer(
                    instance=recipe, context={'request': request}
                )
                return Response(serializer.data, status=201)
        else:
            deleted_count, _ = Favorite.objects.filter(
                recipe=recipe, user=user
            ).delete()

            if deleted_count == 0:
                return Response(
                    {'error': 'Рецепт не в избранном.'}, status=400
                )
            return Response(status=204)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """Добавление или удаление рецепта из списка покупок."""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            is_shopping = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists()

            if is_shopping:
                return Response(
                    {'error': 'Рецепт уже добавлен в корзину.'},
                    status=400
                )
            else:
                ShoppingCart.objects.create(user=user, recipe=recipe)
                serializer = RecipeShortSerializer(
                    recipe, context={'request': request}
                )
                return Response(serializer.data, status=201)
        else:
            deleted_count, _ = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).delete()

            if deleted_count == 0:
                return Response(
                    {'error': 'Рецепта нет в корзине.'}, status=400
                )
            return Response(status=204)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в виде текстового файла."""
        user = request.user
        cart_items = user.shopping_cart.select_related('recipe')
        ingredients = {}

        for item in cart_items:
            recipe = item.recipe
            recipe_ingredients = recipe.recipe_ingredients.select_related(
                'ingredient'
            )

            for ri in recipe_ingredients:
                key = (ri.ingredient.name, ri.ingredient.measurement_unit)
                amount = ri.amount

                if key not in ingredients:
                    ingredients[key] = amount
                else:
                    ingredients[key] += amount

        ing_string = 'Список ингредиентов:\n\n'
        for (name, measurement_unit), amount in ingredients.items():
            ing_string += f'- {name} ({measurement_unit}): {amount};\n'

        response = HttpResponse(ing_string, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


def redirect_to_recipe(request, code):
    """Редирект по короткой ссылке на страницу рецепта."""
    short_link = get_object_or_404(RecipeShortLink, code=code)
    return redirect(f'api/recipes/{short_link.recipe.id}/')
