from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path('cql_faq', views.cql_faq, name='cql_faq'),
    path('tag_list', views.tag_list, name='tag_list'),
    path('search', views.search, name='search'),
    path('search/<str:text_id>/', views.text, name='text'),
    path('search/statistic', views.get_stat, name='statistic'),
    path('search/error-stats', views.get_error_stats, name='error-stats'),
    path('credits/', views.credits, name='credits')
]
