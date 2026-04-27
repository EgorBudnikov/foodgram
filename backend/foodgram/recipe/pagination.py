"""Кастомная пагинация, дзамена имени поля."""
from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Класс кастомной пагинации."""

    page_size_query_param = 'limit'
    page_size = 5
