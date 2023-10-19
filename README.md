# Проект FOODGRAM

Адрес проекта: 158.160.14.162

## Описание

Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Вход в админку

email: admin@yandex.ru
password: admin

#### Технологи

- Python 3.9
- Django 3.2.3
- Django Rest Framework 3.12.4
- Djoser 2.1.0
- Docker
- PostgreSQL
- Gunicorn
- Nginx

#### Документация к API доступна по адресу <http://localhost/api/docs/> после выполнения команды docker-compose up в папке infra.

## Шаблон заполнения .env файла

POSTGRES_USER=*<логин для подключения к базе данных>*

POSTGRES_PASSWORD=*<пароль для подключения к БД>*

POSTGRES_DB=*<имя базы данных>*

DB_HOST=*<название сервиса (контейнера)>*

DB_PORT=*<порт для подключения к БД>*

SECRET_KEY=*<SECRET_KEY Django>*

DEBUG=*<режим отладки>*

ALLOWED_HOSTS=*<список разрешенных хостов>*

PAGE_SIZE=*<количество элементов на странице>*

## Установка

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:pestovaarina/foodgram-project-react.git
```

```
cd infra
```

Запустить проект в контейнерах Docker

```
docker-compose up -d
```
Провести миграции: 

```
docker-compose exec backend python manage.py migrate
```

Создать суперпользователя:

```
docker-compose exec bakend python manage.py createsuperuser
```
Собрать и переместить в volume статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```
```
docker-compose exec backend cp -r /app/static/. /static/
```
## Заполнение базы данными

```
docker-compose exec backend python manage.py loaddata dump.json 
```
## Об авторе
Пестова Арина Витальевна
