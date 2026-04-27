"""Фикстуры для тестирования приложений recipe и users.

Содержит фикстуры для:
- создания валидных и невалидных пользователей
- авторизованного клиента с токеном
- тегов, ингредиентов и рецептов
"""

import pytest
from recipe.models import Ingredient, Tag
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

# ==================== ФИКСТУРЫ ПОЛЬЗОВАТЕЛЕЙ ====================


@pytest.fixture
def user1_valid():
    """Создание 1-го валидного пользователя."""
    return {
        'email': 'root@mail.ru',
        'username': 'root',
        'first_name': 'Белобород',
        'last_name': 'Дракулов',
        'password': 'Qwert43211234'
    }


@pytest.fixture
def user2_valid():
    """Создание 2-го валидного пользователя."""
    return {
        'email': 'root2@mail.ru',
        'username': 'root2',
        'first_name': 'Кирилл',
        'last_name': 'Цветков',
        'password': 'Qwert43211234'
    }


@pytest.fixture
def user_unvalid_email():
    """Невалидный пользователь (дубликат email)."""
    return {
        'email': 'root@mail.ru',
        'username': 'unique_username',
        'first_name': 'Арсений',
        'last_name': 'Крюкохват',
        'password': 'Qwert43211234'
    }


@pytest.fixture
def user_unvalid_username():
    """Невалидный пользователь (дубликат username)."""
    return {
        'email': 'unique_email@mail.ru',
        'username': 'root',
        'first_name': 'Арсений',
        'last_name': 'Крюкохват',
        'password': 'Qwert43211234'
    }


@pytest.fixture
def auth_client(django_user_model):
    """Авторизованный клиент с токеном."""
    def _create_auth_client(user_data):
        user = django_user_model.objects.create_user(**user_data)
        client = APIClient()
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return client, user
    return _create_auth_client


# ==================== ФИКСТУРЫ ТЕГОВ ====================

@pytest.fixture
def tag1():
    """Создание тега "Завтрак"."""
    return Tag.objects.create(name='Завтрак', slug='zavtrak')


# ==================== ФИКСТУРЫ ИНГРЕДИЕНТОВ ====================

@pytest.fixture
def ingredient1():
    """Создание ингредиента "Соль"."""
    return Ingredient.objects.create(name='Соль', measurement_unit='г')


# ==================== ФИКСТУРЫ РЕЦЕПТОВ ====================

@pytest.fixture
def recipe(tag1, ingredient1):
    """Данные для создания рецепта с динамическими ID."""
    image_data = (
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa'
        'AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAA'
        'CklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
    )
    return {
        'ingredients': [{'id': ingredient1.id, 'amount': 55}],
        'tags': [tag1.id],
        'image': image_data,
        'name': 'Солянка',
        'text': 'Вкусный мясной суп',
        'cooking_time': 2,
    }
