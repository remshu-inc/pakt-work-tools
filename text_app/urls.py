from . import views
from . import api
from django.urls import path

urlpatterns = [
    path('corpus/', views.show_files, name='corpus'),
    path('corpus_search/', views.corpus_search, name='corpus_search'),
    path('corpus/<str:language>/', views.show_files, name='language'),
    path('corpus/<str:language>/<str:text_type>/', views.show_files, name='text_type'),
    path('corpus/delete_text', views.delete_text, name='delete_text'),

    path('corpus/<str:language>/<str:text_type>/new_text', views.new_text, name='new_text'),
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/', views.show_text, name='text_view'),
    path('show_text/api/get_classification', api.get_classification, name='get_classification'),
    path('show_text/api/add_empty_token', api.add_empty_token, name='add_empty_token'),
    path('show_text/api/get_text', api.get_text, name='get_text'),
    path('show_text/api/annotation_edit', api.annotation_edit, name='annotation_edit'),

    path('corpus/<str:language>/<str:text_type>/<int:text_id>/asses_edit', views.assessment_form,
         name='asses_edit'),
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/meta_edit', views.meta_form,
         name='meta_edit'),
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/author_edit', views.author_form,
         name='author_edit'),
    path('corpus/<str:language>/<str:text_type>/<int:text_id>/show_raw', views.show_raw,
         name='show_raw'),
]
