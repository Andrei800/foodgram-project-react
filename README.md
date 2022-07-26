![example workflow](https://github.com/ArapatSunny/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# praktikum_new_diplom

### Сайт Foodgram, «Продуктовый помощник».
## Описание:
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Краткое описание запуска проекта
Для работы проекта потребуются установленные Docker и Docker-compose.
При выполнении команды docker-compose up в папке infra запустится сервис frontend, описанный в docker-compose.yml. Он подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.
Проект запустится по адресу http://localhost/

Увидеть спецификацию API: http://localhost/api/docs/

# Сервисы и страницы проекта:
Главная страница, Страница рецепта, Страница пользователя, Подписка на авторов, Список избранного, Список покупок, Фильтрация по тегам, Регистрация и авторизация

### Технологии:
django==3.2
djangorestframework==3.13.1
django-filter==21.1
djoser==2.1.0
drf-extra-fields==3.2.1
drf-writable-nested==0.6.3
drf-yasg==1.20.0
gunicorn==20.0.4
psycopg2-binary==2.9.3
PostgreSQL
nginx

Модели: Ingredient, Tag, Recipe, Favorite, ShoppingCart, IngredientInRecipe


### Как запустить проект:
Клонировать репозиторий:

```
git clone https://github.com/ArapatSunny/foodgram-project-react.git
```
перейти в директорию ../foodgram-project-react/infra/
```
cd infra
```
запустить сборку контейнеров:
```
docker-compose up -d --build
```
Копирование списка ингредиентов и тегов в контейнер с проектом:
```
docker cp ../data/ infra-backend-1:/app
docker cp ../backend/recipes/management/ infra-backend-1:/app/recipes
```
вход в контейнер с проектом:
```
docker-compose exec backend bash
```
применение миграций:
```
python manage.py migrate</br>
python manage.py makemigrations</br>
python manage.py migrate</br>

```
сбор статики
```
python manage.py collectstatic --no-input
```
создание администратора:
```
python manage.py createsuperuser
```
наполнение базы данных ингредиентами и тегами
```
python manage.py import --path './data/ingredients.csv' --model_name 'recipes.Ingredient'
```
```
python manage.py import --path './data/tags.csv' --model_name 'recipes.Tag'
```


### Примеры. Некоторые примеры запросов к API.

Запрос на получение списка рецептов:
```
http://api/recipes/
```
Запрос на получение списка подписок
```
http://api/users/subscription
```

Сайт доступен по адресу: http://51.250.101.226

Админка доступна по адресу: http://51.250.101.226/admin/

Вход в панель администратора: login: vedernikov@gmail.com password: flex3365

Автор проекта:<br/>
Ведерников Андрей<br/>
Студент курса ЯндексПрактикум Python-разработчик<br/>
Факультет Бэкенд.<br/>
