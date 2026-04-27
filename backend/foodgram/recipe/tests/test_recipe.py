"""Тесты для проверки рецептов.

- создание рецептов различными пользователями;
- удаление рецептов различными пользователями.
"""
import pytest


@pytest.mark.django_db
class TestRecipeCreate:
    """Тесты создания рецептов."""

    def test_recipe_create(self, auth_client, user1_valid, recipe):
        """Тест создания рецепта аутентифицированным пользователем."""
        client, user = auth_client(user1_valid)
        response = client.post('/api/recipes/', recipe, format='json')

        assert response.status_code == 201

    def test_recipe_create_not_auth(self, client, recipe):
        """Создание рецепта неаутентифицированным пользователем."""
        response = client.post('/api/recipes/', recipe, format='json')

        assert response.status_code == 401

    def test_recipe_delete(self, auth_client, user1_valid, recipe):
        """Удаление собственного рецепта."""
        client, user = auth_client(user1_valid)

        create_response = client.post('/api/recipes/', recipe, format='json')
        assert create_response.status_code == 201

        assert user.recipes.count() == 1

        recipe_id = user.recipes.first().id
        delete_response = client.delete(f'/api/recipes/{recipe_id}/')

        assert delete_response.status_code == 204

        assert user.recipes.count() == 0

    def test_recipe_delete_not_rights(
            self,
            auth_client,
            user1_valid,
            user2_valid,
            recipe
    ):
        """Удаление не своего рецепта."""
        client, user1 = auth_client(user1_valid)
        client.post('/api/recipes/', recipe, format='json')
        client2, user2 = auth_client(user2_valid)
        recipe_id = user1.recipes.first().id
        response2 = client2.delete(f'/api/recipes/{recipe_id}/')

        assert response2.status_code == 403
