"""Тесты для проверки работы с пользователями.

- создание пользователя, его валидация;
- подписки пользователей;
- отписки от пользователей.
"""
import pytest


@pytest.mark.django_db
class TestUserCreate:
    """Тесты создания пользователей."""

    def test_valid(self, client, user1_valid):
        """Создание пользователя с валидными данными."""
        response = client.post('/api/users/', user1_valid)

        assert response.status_code == 201
        assert 'password' not in response.data

        for field in ('email', 'username', 'first_name', 'last_name'):
            assert user1_valid[field] == response.data[field]

    def test_duplicate_email(self, client, user1_valid, user_unvalid_email):
        """Попытка создать пользователя с существующим email."""
        client.post('/api/users/', user1_valid)

        response = client.post('/api/users/', user_unvalid_email)
        assert response.status_code == 400

    def test_duplicate_username(
            self,
            client,
            user1_valid,
            user_unvalid_username
    ):
        """Попытка создать пользователя с существующим username."""
        client.post('/api/users/', user1_valid)

        response = client.post('/api/users/', user_unvalid_username)
        assert response.status_code == 400


@pytest.mark.django_db
class TestSubscribe:
    """Тесты подписок на пользователей."""

    def test_success(
            self,
            auth_client,
            django_user_model,
            user1_valid,
            user2_valid
    ):
        """Успешная подписка на пользователя."""
        client, user1 = auth_client(user1_valid)
        user2 = django_user_model.objects.create_user(**user2_valid)

        response = client.post(f'/api/users/{user2.id}/subscribe/')

        assert response.status_code == 201
        assert response.data['is_subscribed'] is True
        assert user1.following.filter(id=user2.id).exists()

    def test_self_subscribe(self, auth_client, user1_valid):
        """Нельзя подписаться на самого себя."""
        client, user1 = auth_client(user1_valid)

        response = client.post(f'/api/users/{user1.id}/subscribe/')

        assert response.status_code == 400
        assert 'себя' in str(response.data).lower()

    def test_duplicate_subscribe(
        self,
        auth_client,
        django_user_model,
        user1_valid,
        user2_valid
    ):
        """Нельзя подписаться повторно."""
        client, user1 = auth_client(user1_valid)
        user2 = django_user_model.objects.create_user(**user2_valid)

        response1 = client.post(f'/api/users/{user2.id}/subscribe/')
        assert response1.status_code == 201

        response2 = client.post(f'/api/users/{user2.id}/subscribe/')
        assert response2.status_code == 400

    def test_unauthenticated(self, client, django_user_model, user2_valid):
        """Неавторизованный пользователь не может подписаться."""
        user2 = django_user_model.objects.create_user(**user2_valid)

        response = client.post(f'/api/users/{user2.id}/subscribe/')

        assert response.status_code == 401

    def test_non_existing_user(self, auth_client, user1_valid):
        """Подписка на несуществующего пользователя."""
        client, _ = auth_client(user1_valid)
        non_existent_id = 99999

        response = client.post(f'/api/users/{non_existent_id}/subscribe/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestUnsubscribe:
    """Тесты отписки от пользователей."""

    def test_success(
        self,
        auth_client,
        django_user_model,
        user1_valid,
        user2_valid
    ):
        """Успешная отписка от пользователя."""
        client, user1 = auth_client(user1_valid)
        user2 = django_user_model.objects.create_user(**user2_valid)

        client.post(f'/api/users/{user2.id}/subscribe/')
        assert user1.following.filter(id=user2.id).exists()

        response = client.delete(f'/api/users/{user2.id}/subscribe/')

        assert response.status_code == 204
        assert not user1.following.filter(id=user2.id).exists()

    def test_not_subscribed(
            self,
            auth_client,
            django_user_model,
            user1_valid,
            user2_valid
    ):
        """Отписка от пользователя, на которого не подписан."""
        client, _ = auth_client(user1_valid)
        user2 = django_user_model.objects.create_user(**user2_valid)

        response = client.delete(f'/api/users/{user2.id}/subscribe/')

        assert response.status_code == 400

    def test_self_unsubscribe(self, auth_client, user1_valid):
        """Отписка от самого себя."""
        client, user1 = auth_client(user1_valid)

        response = client.delete(f'/api/users/{user1.id}/subscribe/')

        assert response.status_code == 400

    def test_unauthenticated(self, client, django_user_model, user2_valid):
        """Неавторизованный пользователь не может отписаться."""
        user2 = django_user_model.objects.create_user(**user2_valid)

        response = client.delete(f'/api/users/{user2.id}/subscribe/')

        assert response.status_code == 401

    def test_non_existing_user(self, auth_client, user1_valid):
        """Отписка от несуществующего пользователя."""
        client, _ = auth_client(user1_valid)
        non_existent_id = 99999

        response = client.delete(f'/api/users/{non_existent_id}/subscribe/')

        assert response.status_code == 404
