from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path('search', views.search, name='search'),
]