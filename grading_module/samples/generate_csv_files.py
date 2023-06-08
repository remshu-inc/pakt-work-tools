"""
Пример генерации файлов с исходными данными для обучения
"""
from grading_module.common import GrossModelDataTo_scv
from pakt_work_tools.settings import DATABASES

if __name__ == "__main__":
    # берем подключение к БД из настроек приложения Django
    connection = DATABASES['default']
    GrossModelDataTo_scv("data.csv", connection['USER'], connection['PASSWORD'], connection['HOST'], connection['NAME'])
