from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    
    # Тестовый показ
    path('search1/', views.index),
    path('search1/Reise/', views.index),
]