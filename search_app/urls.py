from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path('cql_faq', views.cql_faq, name='cql_faq'),
    path('search', views.search, name='search'),
    path('search/statistic', views.get_stat, name='statistic')
]