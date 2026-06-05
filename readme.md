# TeamFinder

TeamFinder - Django-приложение для поиска участников в pet-проекты. В проекте реализованы регистрация и вход по email, профили пользователей, навыки пользователей, создание и редактирование проектов, участие в проектах, завершение проектов, список участников платформы и вариант 3 задания: необходимые навыки проектов с фильтрацией проектов по навыкам.

## Технологии

- Python 3.11+
- Django 5.2
- PostgreSQL
- Pillow
- psycopg
- python-decouple

## Быстрый запуск

1. Создайте и активируйте виртуальное окружение:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` по примеру `.env_example`. Для выбранного варианта должно быть указано:

```env
TASK_VERSION=3
```

4. Запустите PostgreSQL:

```bash
docker compose up -d
```

5. Примените миграции:

```bash
python manage.py migrate
```

6. Создайте демонстрационные данные:

```bash
python manage.py seed_data
```

7. Запустите сервер:

```bash
python manage.py runserver
```

Приложение будет доступно по адресу http://127.0.0.1:8000/.

## Тестовые аккаунты

После выполнения `python manage.py seed_data` доступны аккаунты:

- `maria@yandex.ru` / `password`
- `alex@example.com` / `password`
- `dmitry@example.com` / `password`
- `olga@example.com` / `password`
- `admin@example.com` / `admin`

## Проверка проекта

Запуск автоматических тестов:

```bash
python manage.py test
```

Проверка Django:

```bash
python manage.py check
```

Для локальной проверки без PostgreSQL можно временно использовать SQLite:

```bash
$env:USE_SQLITE="True"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Основные страницы:

- `/projects/list/` - список проектов и фильтр по необходимым навыкам
- `/projects/create-project/` - создание проекта
- `/projects/<id>/` - страница проекта
- `/users/list/` - список участников
- `/users/<id>/` - профиль пользователя
- `/users/skills/` - поиск навыков для профиля
- `/users/register/` - регистрация
- `/users/login/` - вход
- `/users/change-password/` - смена пароля

## Реализованный вариант

В проекте выбран вариант 3: "Необходимые навыки" проектов и фильтрация проектов по навыкам.

На странице проекта владелец может добавлять и удалять необходимые навыки без перезагрузки страницы. Поиск навыков работает через `/projects/skills/?q=<строка>`, добавление - через `/projects/<id>/skills/add/`, удаление - через `/projects/<id>/skills/<skill_id>/remove/`.

На странице `/projects/list/` доступен фильтр по навыкам. Активный фильтр передается через query-параметр `skill`.
