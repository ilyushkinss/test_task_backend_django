# API Интернет-магазина продуктов

Проект реализует RESTful API для интернет-магазина продуктов на базе Django Rest Framework.

## Функциональность

### Категории и подкатегории
- Создание, редактирование, удаление категорий и подкатегорий через админку
- Каждая категория/подкатегория имеет: наименование, slug, изображение
- Подкатегории связаны с родительской категорией
- Эндпоинт для просмотра всех категорий с подкатегориями (с пагинацией)

### Продукты
- Создание, редактирование, удаление продуктов через админку
- Продукты относятся к подкатегориям и имеют: наименование, slug, цену
- Поддержка изображений в 3-х размерах (маленькое, среднее, большое)
- Эндпоинт вывода продуктов с пагинацией
- В выводе продукта: наименование, slug, категория, подкатегория, цена, список изображений

### Корзина
- Добавление, изменение количества, удаление продукта из корзины
- Вывод состава корзины с подсчетом количества и общей стоимости
- Полная очистка корзины
- Доступ только авторизованным пользователям к своей корзине

### Авторизация
- JWT токен аутентификация
- Регистрация новых пользователей
- Обновление access токена через refresh токен

## Технологии

- Django 5.2.7
- Django Rest Framework 3.16.1
- Django REST Framework SimpleJWT 5.5.1
- drf-spectacular (Swagger/OpenAPI)
- Pillow (работа с изображениями)
- SQLite (БД)

## Установка и запуск

1. Клонируйте репозиторий https://github.com/ilyushkinss/test_task_backend_django

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # на Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Примените миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Загрузите фикстуры (опционально):
```bash
python manage.py loaddata shop/fixtures/initial_data.json
```

7. Запустите сервер:
```bash
python manage.py runserver
```

## Структура API

### Базовый URL
```
http://localhost:8000/api/v1/
```

### Эндпоинты

#### Категории
- `GET /api/v1/categories/` - список всех категорий с подкатегориями
- `GET /api/v1/categories/{slug}/` - детали категории

#### Продукты
- `GET /api/v1/products/` - список продуктов (с пагинацией)
- `GET /api/v1/products/{slug}/` - детали продукта
- Фильтры: `?category={slug}` или `?subcategory={slug}`

#### Корзина (требуется авторизация)
- `GET /api/v1/cart/` - просмотр корзины
- `POST /api/v1/cart/items/` - добавление продукта
  ```json
  {
    "product_id": 1,
    "quantity": 2
  }
  ```
- `PATCH /api/v1/cart/items/{id}/` - изменение количества
  ```json
  {
    "quantity": 5
  }
  ```
- `DELETE /api/v1/cart/items/{id}/` - удаление продукта из корзины
- `DELETE /api/v1/cart/{id}/` - очистка корзины (id можно передать текущей корзины)

#### Авторизация
- `POST /api/v1/auth/register/` - регистрация
  ```json
  {
    "username": "user",
    "password": "password",
    "email": "user@example.com"
  }
  ```
- `POST /api/v1/auth/token/` - получение токенов
  ```json
  {
    "username": "user",
    "password": "password"
  }
  ```
- `POST /api/v1/auth/token/refresh/` - обновление access токена
  ```json
  {
    "refresh": "refresh_token"
  }
  ```


## Админ-панель

Доступна по адресу: http://localhost:8000/admin/

### Данные для входа
Используйте данные созданного суперпользователя.

По умолчанию создан пользователь:
- Username: `admin`
- Password: `admin123`

## Тестирование

Запуск всех тестов:
```bash
python manage.py test shop.tests
```

Тесты покрывают:
- GET запросы к категориям и продуктам
- POST запросы для регистрации и получения токенов
- Работу с корзиной (добавление, изменение, удаление, очистка)

## Структура проекта

```
product_shop/
├── config/           # Настройки Django проекта
│   ├── settings.py   # Конфигурация проекта
│   ├── urls.py       # URL маршруты
│   └── ...
├── shop/             # Приложение магазина
│   ├── models.py     # Модели данных
│   ├── serializers.py # Сериализаторы DRF
│   ├── views.py      # ViewSets
│   ├── urls.py       # URL маршруты приложения
│   ├── admin.py      # Админ-панель
│   ├── tests.py      # Тесты
│   ├── fixtures/     # Фикстуры данных
│   └── auth_views.py # Views для авторизации
├── media/            # Загруженные файлы
├── db.sqlite3        # База данных
├── manage.py         # Django управление
├── requirements.txt  # Зависимости
└── README.md         # Документация
```

## Фикстуры

Фикстуры содержат тестовые данные:
- 2 категории (Овощи, Фрукты)
- 4 подкатегории (Корнеплоды, Листовые, Яблоки, Цитрусовые)
- 8 продуктов с ценами и описаниями

## Использование API

### Пример работы с корзиной

1. Зарегистрируйтесь:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass","email":"test@test.com"}'
```

2. Получите токен:
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

3. Добавьте товар в корзину:
```bash
curl -X POST http://localhost:8000/api/v1/cart/items/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

4. Измените количество:
```bash
curl -X PATCH http://localhost:8000/api/v1/cart/items/ITEM_ID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":5}'
```

5. Удалите товар из корзины:
```bash
curl -X DELETE http://localhost:8000/api/v1/cart/items/ITEM_ID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

6. Очистите корзину:
```bash
curl -X DELETE http://localhost:8000/api/v1/cart/CART_ID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Swagger документация

Документация API доступна по следующим ссылкам:

**Swagger UI**: http://localhost:8000/api/schema/swagger-ui/

**ReDoc**: http://localhost:8000/api/schema/redoc/

После запуска сервера (`python manage.py runserver`) откройте любую из этих ссылок в браузере для просмотра интерактивной документации API.

## Лицензия

Проект создан в учебных целях.

