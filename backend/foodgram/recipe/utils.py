"""Функция получения кода для короткой ссылки."""
import secrets
import string


def generate_short_code(length=3):
    """Генерация кода для короткой ссылки рецептов."""
    str_ = string.ascii_letters + string.digits
    return ''.join(secrets.choice(str_) for _ in range(length))
