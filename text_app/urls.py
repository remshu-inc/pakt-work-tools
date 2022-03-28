from . import views
from . import api
from django.urls import path

urlpatterns = [
    path('corpus/', views.show_files, name='corpus'),
    path('corpus_search/', views.corpus_search, name='corpus_search'),
    path('corpus/<str:language>/', views.show_files, name='language'),
    path('corpus/<str:language>/<str:text_type>/', views.show_files, name='text_type'),
    path('corpus/<str:language>/<str:text_type>/new_text', views.new_text, name='new_text'),
    # path('corpus/<str:language>/<str:text_type>/<int:text_id>', views.show_text, name='show_text'),
    path('corpus/<str:language_test>/<str:text_type_test>/<int:text_id>/pos/<int:pos>/error/<int:error>/tag_lang/<str:language>', views.show_text),
    path('corpus/<str:language_test>/<str:text_type_test>/<int:text_id>/', views.show_text),
    path('show_text/api/add_empty_token', api.add_empty_token),
    path('show_text/api/get_text', api.get_text),
]