from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('manage/', views.manage, name='manage'),
    path('manage/signup/', views.signup, name='signup'),
    path('manage/group_creation/', views.group_creation, name='group_creation')
]