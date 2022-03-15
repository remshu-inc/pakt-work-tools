from . import views
from django.urls import path

urlpatterns = [
    path('corpus/', views.show_files, name='home'),
    path('corpus/<str:language>/', views.show_files, name='language'),
    path('corpus/<str:language>/<str:text_type>/', views.show_files, name='text_type'),
    path('new_text/', views.new_file, name='new_text'),
    path('show_text+id=<int:text_id>/', views.show_text),
    path('show_text/', views.show_text)
]