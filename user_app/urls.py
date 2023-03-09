from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('manage/', views.manage, name='manage'),
    path('manage/signup/', views.signup, name='signup'),
    path('manage/change_password', views.change_password, name='change_password'),
    path('manage/signup_teacher/', views.signup_teacher, name='signup_teacher'),
    path('manage/group_creation/', views.group_creation, name='group_creation'),
    path('manage/group_modify/', views.group_selection, name = 'group_selection'),
    path('manage/group_modify/<int:group_id>/', views.group_modify, name = 'group_modify'),
    # path('manage/group_modify/<int:group_id>', views.group_selection, name = 'group_selection'),
    path('manage/tasks_info/<int:user_id>', views.tasks_info, name = 'tasks_info')
]