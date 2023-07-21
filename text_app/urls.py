'''
Project: pakt-work-tools
File name: urls.py
Description: Перечень URL для функций работы с текстами
'''

from . import views
from . import api
from django.urls import path

urlpatterns = [
    #* Управление текстами
    # Просмотр досутпных текстов
    path('corpus/', views.show_files, name='corpus'),
    path('corpus/<str:language>/', views.show_files, name='language'),
    path('corpus/<str:language>/<str:text_type>/', views.show_files, name='text_type'),
    # Открытие выбранного текста
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/', views.show_text, name='text_view'),
    # Создание нового текста 
    path('corpus/<str:language>/<str:text_type>/new_text', views.new_text, name='new_text'),
    # Поиск по корпусу
    path('corpus_search/', views.corpus_search, name='corpus_search'),
    #*  Работа с выбранным текстом
    # Удаление текста из корпуса
    path('corpus/delete_text', views.delete_text, name='delete_text'),
    #** URL's для обработки запросов со стороны фронта
    # Получение классификации тегов применимой к тексту
    path('show_text/api/get_classification', api.get_classification, name='get_classification'),
    # Создание пустого токена
    path('show_text/api/add_empty_token', api.add_empty_token, name='add_empty_token'),
    # Получение содержимого текста из БД
    path('show_text/api/get_text', api.get_text, name='get_text'),
    # Создание/удаление аннотаций
    path('show_text/api/annotation_edit', api.annotation_edit, name='annotation_edit'),
     #** Формы
     # Оценка текста
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/asses_edit', views.assessment_form,
         name='asses_edit'),
     # Изменение метаданных
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/meta_edit', views.meta_form,
         name='meta_edit'),
     # Изменение информации об авторе
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/author_edit', views.author_form,
         name='author_edit'),
     #** Иное
     # Отображение исходного текста
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/show_raw', views.show_raw,
         name='show_raw'),
     # Частеречная разметка
    path('part_of_speech', api.process_part_of_speech, name="part_of_speech")
]
