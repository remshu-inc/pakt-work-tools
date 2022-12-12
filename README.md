# PAKT Work Tools
Комплекс инструментов для работы с петрозаводским аннотированным корпусом

## Возможности
### Аннотирование корпуса
* Преподаватель
  * Загрузка работ от лица студента
  * Просмотр и удаление любых работ
  * ~~Аннтирование всех текстов~~
  * ~~Возможность давать доступ студентам для аннотирования текста~~

* Студент
  * Загрузка новых работ от своего лица
  * Просмотр и удаление только своих работ
  * ~~Аннотация только разрешенных текстов~~


### Поиск по корпусу
РАЗРАБОТКА


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
`pip install -r pakt-work-tools\requirements.txt`
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
11. Создание миграций:
	1. Если папка `migrations` пуста:
    	1. `python manage.py makemigrations text_app`
		2. `python manage.py makemigrations user_app`
		3. `python manage.py makemigrations right_app`
	2. Иначе выполните скрипт `python drop_migrations.py` и выполните пункт 11.1
12. Запустите миграцию
`python manage.py migrate`
13. При наличии дампа базы данных восстановите его в подключеннную к сервису базу данных
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