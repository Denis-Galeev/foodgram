[![.github/workflows/main.yml](https://github.com/Denis-Galeev/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Denis-Galeev/foodgram/actions/workflows/main.yml)

<p align="center">
 <img src="frontend/public/favicon.png" width="100"/>
</p>

# Проект Foodgram 

## Описание проекта
«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Пользователь может скачать свой список покупок в формате PDF.

## Стек технологий

**Backend:** 

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%230c4b34?style=for-the-badge&logo=django&logoColor=white
)
![DjangoREST](https://img.shields.io/badge/framework-%23a30000?style=for-the-badge&logo=django&logoColor=white&label=rest&labelColor=%232c2c2c
)
![Postgres](https://img.shields.io/badge/PostgreSQL-336690?style=for-the-badge&logo=postgresql&logoColor=white&logoSize=auto
)

**Frontend**

![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![React](https://img.shields.io/badge/react-%2320232a?style=for-the-badge&logo=react&logoColor=%2361dafb
)

**Инфраструктура:**

![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

## Для запуска проекта из образов с Docker hub

Cоздаём папку проекта `foodgram` и переходим в нее:

```bash
mkdir foodgram
cd foodgram
```

В папку проекта копируем (или создаём и заполняем) файл `docker-compose.production.yml` и запускаем его:

```bash
sudo docker compose -f docker-compose.production.yml up -d
```

Будут скачаны образы из dockerhub, на их основе поднимуться необходимые контейнеры, томы и сети.


## Для запуска проекта из исходников GitHub

Клонируем себе репозиторий: 

```bash 
git clone git@github.com:Denis-Galeev/foodgram.git
```

Выполняем запуск:

```bash
sudo docker compose -f docker-compose.yml up -d
```

## После запуска: Миграции, сбор статистики

После запуска нужно выполнить сбор статистики и миграцию для бэкенда. Статистика фронтенда собирается во время запуска контейнера, после чего он останавливается. 

```bash
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py migrate

sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py collectstatic

sudo docker compose -f [имя-файла-docker-compose.yml] exec backend cp -r /app/collected_static/. /static/static/
```

Теперь проект доступен на: 

```
http://localhost:7000/
```

Документация будет доступна по адресу: 

```
http://localhost:7000/api_docs/
```

## Описание переменных окружения

Ниже пример файла .env c переменными окружения, необходимыми для запуска приложения

```bash
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DEBUG=False
SECRET_KEY=django_secret_key_example
ALLOWED_HOSTS=yoursite.example.com,localhost,127.0.0.1
USE_SQLITE=false
```


## Остановка оркестра контейнеров

В окне, где был запуск **Ctrl+С** или в другом окне:

```bash
sudo docker compose -f docker-compose.yml down  # с их удалением
sudo docker compose -f docker-compose.yml stop  # без удаления
```

## Автор

## Автор:

**Имя:** Денис Галеев  
**Почта:** dmdenis74chel@yandex.ru  
**Telegram:** @Denis_74_chel 