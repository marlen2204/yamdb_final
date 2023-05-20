![Github CI/CD](![example workflow](https://img.shields.io/appveyor/build/marlen2204/yamdb_final))

# Infra_sp2
- [x] заполнить файл c workflow
- [ ] добавить в secrets секреты
### Описание
По сути это проект api_ymdb упакованный в docker-compose, с настроенным nginx  и postgres в качестве базы данных
Проект YaMDb собирает отзывы пользователей на произведения.
### Технологии
Python 3.1
Django 3.2
DRF 3.12.4
PyJWT 2.1.0
docker-compose 3.3
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
```
python3 -m venv venv
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```
### Запуск проекта в основном режиме
- Предполагаетсся, что docker-compose 3.3 уже установлен
- Заполнтие .env  в директории infra по шаблону:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=''
POSTGRES_PASSWORD=''
DB_HOST=db
DB_PORT=5432
SECRET_KEY = ''
```
- запускаем:  ``` docker-compose up -d --build ``` в директории infra
-  создаем и применяем миграции 
``` 
docker-compose exec web python manage.py migrate
```
- ИЛИ создаем миграции для каждого приложения отдельно, а потом выполняем миграцию
```
docker-compose exec web python manage.py makemigrations users
docker-compose exec web python manage.py makemigrations reviews
```
### Итог
Сервер поднят и доступен на 80 порте.
#### Чтобы заполнить базу тестовыми данными выполните:
```
docker-compose exec web python manage.py load fixtures.json
```
