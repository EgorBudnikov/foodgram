"""Урлы и эндпоинты приложения."""
from django.contrib import admin
from django.urls import include, path
from recipe.views import (IngredientViewSet, RecipeViewSet, TagsViewSet,
                          redirect_to_recipe)
from rest_framework import routers
from users.views import (UserViewSet, change_password, token_delete,
                         token_obtain)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('', include(router.urls)),
        path('auth/token/login/', token_obtain, name='token_obtain'),
        path('auth/token/logout/', token_delete, name='token_delete'),
        path('users/set_password/', change_password, name='change_password'),
    ])),
    path('s/<str:code>/', redirect_to_recipe, name='redirect_to_recipe'),
]
