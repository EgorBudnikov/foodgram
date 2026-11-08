# Foodgram — социальная сеть для любителей готовить

Foodgram — веб-приложение, в котором пользователи публикуют рецепты, подписываются на авторов, сохраняют понравившиеся блюда и формируют список покупок. Проект состоит из React-фронтенда, REST API на Django и инфраструктуры Docker Compose с PostgreSQL и Nginx.

## Возможности

- регистрация пользователей и аутентификация по токену;
- просмотр профилей авторов и подписка на них;
- создание, редактирование и удаление собственных рецептов;
- загрузка изображения, указание ингредиентов, тегов и времени приготовления;
- фильтрация рецептов по тегам, автору, избранному и списку покупок;
- добавление рецептов в избранное;
- формирование списка покупок;
- выгрузка общего списка ингредиентов в текстовый файл;
- поиск ингредиентов по началу названия;
- генерация коротких ссылок на рецепты;
- административная панель Django;
- интерактивная API-документация.

## Стек технологий

### Backend

- Python 3.12
- Django 6
- Django REST Framework
- Djoser
- PostgreSQL
- Gunicorn
- Pytest и pytest-django
- Flake8

### Frontend и инфраструктура

- React
- Node.js 16
- Docker и Docker Compose
- Nginx
- GitHub Actions


## Быстрый запуск в Docker

### Требования

- Docker
- Docker Compose
- свободный порт `80`

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/EgorBudnikov/foodgram.git
cd foodgram
```

### 2. Создайте файл окружения

В корне проекта создайте файл `.env`:

```env
# Django
DJANGO_SECRET_KEY=change-me-to-a-long-random-secret
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1

# PostgreSQL
DATABASE_NAME=foodgram
DATABASE_USERNAME=foodgram_user
DATABASE_PASSWORD=strong_password
DATABASE_HOST=postgres
DATABASE_PORT=5432
```

> Для запуска в Docker значение `DATABASE_HOST` должно соответствовать имени сервиса базы данных — `postgres`.

### 3. Запустите контейнеры

```bash
docker compose up --build -d
```

Во время старта backend-контейнер применяет миграции и собирает статические файлы автоматически.

### 4. Откройте приложение

После успешного запуска будут доступны:

- приложение: `http://localhost/`;
- API: `http://localhost/api/`;
- интерактивная документация API: `http://localhost/api/docs/`;
- админ-панель: `http://localhost/admin/`.

Для остановки окружения выполните:

```bash
docker compose down
```

Чтобы удалить данные PostgreSQL вместе с контейнерами:

```bash
docker compose down -v
```

## Локальная разработка backend

### Требования

- Python 3.12 или совместимая версия;
- PostgreSQL;
- виртуальное окружение Python.

### Установка зависимостей

```bash
cd backend/foodgram
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создайте `.env` рядом с `manage.py`, укажите параметры подключения к PostgreSQL и примените миграции:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Локальная разработка frontend

```bash
cd frontend
npm ci --legacy-peer-deps
npm start
```

Для production-сборки:

```bash
npm run build
```

## Основные API-маршруты

| Маршрут | Назначение |
| --- | --- |
| `/api/users/` | Пользователи, профили и подписки |
| `/api/auth/token/login/` | Получение токена авторизации |
| `/api/auth/token/logout/` | Отзыв токена |
| `/api/users/set_password/` | Смена пароля |
| `/api/tags/` | Список тегов рецептов |
| `/api/ingredients/` | Список и поиск ингредиентов |
| `/api/recipes/` | Просмотр и управление рецептами |
| `/api/recipes/{id}/favorite/` | Добавление или удаление из избранного |
| `/api/recipes/{id}/shopping_cart/` | Добавление или удаление из списка покупок |
| `/api/recipes/download_shopping_cart/` | Скачивание списка покупок |
| `/api/recipes/{id}/get-link/` | Получение короткой ссылки на рецепт |

Полная спецификация API доступна после запуска проекта по адресу `/api/docs/`.

## Фильтрация рецептов

Эндпоинт `GET /api/recipes/` поддерживает параметры:

```text
?tags=breakfast&tags=lunch
?author=1
?is_favorited=1
?is_in_shopping_cart=1
?limit=10&page=2
```

- `tags` — один или несколько slug тегов;
- `author` — идентификатор автора;
- `is_favorited=1` — рецепты из избранного текущего пользователя;
- `is_in_shopping_cart=1` — рецепты из списка покупок текущего пользователя;
- `limit` и `page` — параметры пагинации.

## Тестирование и проверка кода

### Backend

```bash
cd backend/foodgram
pytest
```

Проверка стиля:

```bash
flake8 backend/
```

### Frontend

```bash
cd frontend
CI=true npm run test
```

## CI/CD

При отправке изменений в ветку `main` GitHub Actions выполняет:

1. проверку backend-кода с помощью Flake8;
2. запуск backend-тестов на PostgreSQL;
3. установку зависимостей и тестирование frontend;
4. сборку Docker-образов backend, frontend и Nginx;
5. публикацию образов в Docker Hub;
6. развёртывание на сервере по SSH с использованием production-конфигурации.

Для production-развёртывания используются секреты GitHub Actions:

```text
DOCKER_USERNAME
DOCKER_PASSWORD
HOST
USER
SSH_KEY
```

Также production-конфигурация ожидает переменную `USERNAME_DOC` в `.env` — она используется для формирования имён Docker-образов.

## Production-запуск

На сервере подготовьте `.env` с параметрами Django, PostgreSQL и Docker Hub:

```env
DJANGO_SECRET_KEY=change-me-to-a-long-random-secret
DJANGO_ALLOWED_HOSTS=your-domain.example
DATABASE_NAME=foodgram
DATABASE_USERNAME=foodgram_user
DATABASE_PASSWORD=strong_password
DATABASE_HOST=postgres
DATABASE_PORT=5432
USERNAME_DOC=your-dockerhub-username
```

Запустите сервисы:

```bash
docker compose -f docker-compose.production.yml up -d
```

В production-конфигурации Nginx публикует приложение на порту `8080`.

## Полезные команды Docker

```bash
# Просмотреть состояние контейнеров
docker compose ps

# Посмотреть логи backend
 docker compose logs -f backend

# Выполнить команду Django внутри контейнера
docker compose exec backend python manage.py createsuperuser

# Применить миграции вручную
docker compose exec backend python manage.py migrate
```

## Автор

[Egor Budnikov](https://github.com/EgorBudnikov)
