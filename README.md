# PAKT Work Tools
Комплекс инструментов для работы с петрозаводским аннотированным корпусом

## Возможности
### Аннотирование корпуса
* Преподаватель
  * Загрузка работ от лица студента
  * Просмотр и удаление любых работ
  * Аннтирование всех текстов
  * ~~Возможность давать доступ студентам для аннотирования текста~~

* Студент
  * Загрузка новых работ от своего лица
  * Просмотр и удаление только своих работ
  * ~~Аннотация только разрешенных текстов~~


### Поиск по корпусу
Модуль search_app предоставляет пользователю интерфейс для поиска по корпусу с использованием язык [Corpus Query Language](https://www.sketchengine.eu/documentation/corpus-querying/).

### Выгрузка корпуса
Документация и скрипты для выгрузки корпуса размещены в [каталоге модуля](csv-dump).

### Модуль построения оценок
Документация и скрипты обучения и использования модуля построения оценок размещены в [каталоге модуля](grading_module).

## Установка
**Пре-установка**
1. Установите [GIT](https://git-scm.com/downloads)
2. Установите [Python3](https://www.python.org/downloads/)
3. Установите и настройте [MySQL Server](https://dev.mysql.com/downloads/mysql/)


**Установка**
1. Создайте папку для проекта
2. Установите виртуальное окружение `pip install virtualenv`
3. Создайте виртуальное окружение pakt `python -m venv pakt`
4. Создайте пустую базу данных без структуры
5. Запустите виртуальное окружение
(Для Windows:`.\pakt\Scripts\Activate.ps1`)
6. Склонируйте проект с git
`git clone https://github.com/remshu/pakt-work-tools.git` и перейдите в папку
7. Установите все требуемые библиотеки
`pip install -r requirements.txt`
8. Создайте необходимые директории `python create_folders.py`
9. Выберите или задайте путь к папкам временных файлов в `pakt_work_tools\settings.py`, раздел `Other settings`
```
#Other settings

SEARCH_TMP_FOLDER_LOCAL = 'search_app/tmp/'
SEARCH_TMP_FOLDER_SERVER = 'var/www/lingo/pakt-work-tools/search_app/tmp/'
SEARCH_TMP_FOLDER = SEARCH_TMP_FOLDER_SERVER
```
10. Измените данные для работы с БД в `pakt_work_tools\settings.py`
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'name',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'CHARSET': 'utf8mb4',
    }
}
```
 * ENGINE - Встроенная сервернная база данных для использования(оставить как есть)
 * NAME - Имя созданной базы данных из пункта 4
 * USER - Имя пользователя, используемое при установке и настройки системы управления базами данных
 * PASSWORD - Пароль пользователя, используемый при установке и настройки системы управления базами данных
 * HOST - Хост, который используется при подключении к базе данных(по умолчанию: 127.0.0.1)
 * PORT - Порт, используемый при установке и настройки системы управления базами данных(по умолчанию: 3306)
11. Создание миграций:
	1. Если папка `migrations` пуста или отсутствует:
    	1. `python manage.py makemigrations text_app`
		2. `python manage.py makemigrations user_app`
		3. `python manage.py makemigrations right_app`
		4. `python manage.py makemigrations search_app`
	2. Иначе выполните скрипт `python drop_migrations.py` и выполните пункт 11.1
12. Запустите миграцию
`python manage.py migrate`
13. При наличии дампа базы данных восстановите его в подключенную к сервису базу данных
14. Запустите сервер `python manage.py runserver`

## ***Дополнительно***
### *Создание корректного дампа базы данных:*
```
mysqldump -uuser -ppassword database_name --no-tablespaces --complete-insert --no-create-info --lock-tables=True --routines --ignore-table=lingo.auth_group --ignore-table=lingo.auth_group_permissions --ignore-table=lingo.auth_permission --ignore-table=lingo.django_admin_log --ignore-table=lingo.django_content_type --ignore-table=lingo.django_migrations --ignore-table=lingo.django_session  > dump.sql
```
### *Восстановление дампа базы данных:*
```
mysql -uuser -ppassword database_name < dump.sql
```

### Запуск тестов с оценкой покрытия
```shell
coverage run --source='.' manage.py test --keepdb
coverage html --omit="search_app/*"
```
