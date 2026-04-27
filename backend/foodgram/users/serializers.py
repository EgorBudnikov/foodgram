"""Сериализаторы для АПИ.

- валидация данных при создании пользователя;
- валидация при подписках;
- получение пароля;
- получение токена;
"""
import base64

from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from recipe.serializers import RecipeShortSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для списка и создания."""

    password = serializers.CharField(write_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        """Установка модели и ее полей сериализатора."""

        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'password', 'avatar')
        read_only_fields = ('id',)
        extra_kwargs = {'avatar': {'required': False}}

    def create(self, validated_data):
        """Установка пароля пользователя."""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_avatar(self, obj):
        """Получение ссылки аватара."""
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def to_representation(self, instance):
        """Преобразует объект в словарь, удаляя avatar при POST-запросе."""
        representation = super().to_representation(instance)

        request = self.context.get('request')
        if request and request.method == 'POST':
            representation.pop('avatar', None)
        return representation


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для получения инфо о пользователе."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        """Установка модели и ее полей сериализатора."""

        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        """Получение подиски на пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(id=obj.id).exists()
        return False

    def get_avatar(self, obj):
        """Получение ссылки аватара."""
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор обработки подписок."""

    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """Установка модели и ее полей сериализатора."""

        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
                  'last_name', 'avatar', 'recipes',
                  'is_subscribed', 'recipes_count'
        )
        read_only_fields = ('id',)

    def get_recipes_count(self, obj):
        """Получение поля количества рецептов пользователя."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Получение поля рецептов пользователя."""
        recipes = obj.recipes.all()

        recipes_limit = self.context.get('recipes_limit')
        recipes = recipes[:recipes_limit]

        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_is_subscribed(self, obj):
        """Получение поля подписки на пользователя."""
        return True


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на пользователей."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Установка модели и ее полей сериализатора."""

        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar']

    def get_recipes(self, obj):
        """Получение поля рецептов пользователя."""
        recipes = obj.recipes.all()

        recipes_limit = self.context.get('recipes_limit', 3)
        recipes = recipes[:recipes_limit]

        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        """Получение поля количества рецептов пользователя."""
        recipes_count = obj.recipes.count()
        return recipes_count

    def get_is_subscribed(self, obj):
        """Получение поля подписки на пользователя."""
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            return request.user.following.filter(pk=obj.id).exists()
        return False


class TokenSerializer(serializers.Serializer):
    """Серилизатор для получения токена."""

    email = serializers.EmailField()
    password = serializers.CharField(max_length=150)

    def validate(self, data):
        """Валидация пользлователя перед токеном."""
        email = data.get('email')
        password = data.get('password')

        user = get_object_or_404(User, email=email)

        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError('Неверный email или пароль')

        data['user'] = user
        return data

    def create(self, validated_data):
        """Получение токена."""
        user = validated_data.get('user')
        token, created = Token.objects.get_or_create(user=user)
        return token.key


class PasswordSerializers(serializers.Serializer):
    """Сериализатор для смены пароля."""

    new_password = serializers.CharField(max_length=150, write_only=True)
    current_password = serializers.CharField(max_length=150, write_only=True)

    def validate(self, data):
        """Проверка пользователя с таким паролем."""
        request = self.context.get('request')
        user = request.user

        current_password = data.get('current_password')

        if not user.check_password(current_password):
            raise serializers.ValidationError('Старый пароль указан не верно.')
        return data

    def save(self):
        """Функция замены старого пароля."""
        request = self.context.get('request')
        user = request.user
        new_password = self.validated_data.get('new_password')

        user.set_password(new_password)
        user.save()
        return user


class AvatarSerializer(serializers.Serializer):
    """Сериализатор  установки аватара."""

    avatar = serializers.CharField()

    def save(self, user, request):
        """Сохранение аватара пользователя."""
        avatar_data = self.validated_data.get('avatar')
        format, img = avatar_data.split(';base64,')
        file_data = base64.b64decode(img)
        ext = format.split('/')[-1]

        user.avatar.save(f'avatar.{ext}', ContentFile(file_data), save=True)

        return request.build_absolute_uri(user.avatar.url)
