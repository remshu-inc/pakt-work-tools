from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('manage/', views.manage, name='manage'),
    path('manage/signup/', views.signup, name='signup'),
    path('manage/change_password_student/', views.change_password_student, name='change_password_student'),
    path('manage/change_password/', views.change_password_self, name='change_password_self'),
    path('manage/signup_teacher/', views.signup_teacher, name='signup_teacher'),
    path('manage/group_creation/', views.group_creation, name='group_creation'),
    path('manage/group_modify/', views.group_selection, name='group_selection'),
    path('manage/group_modify/<int:group_id>/', views.group_modify, name='group_modify'),
    path('manage/group_modify/<int:group_id>/delete_student/<int:student_id>/', views.group_delete_student, name='group_delete_student'),
    path('manage/group_modify/<int:group_id>/add_student/<int:student_id>/', views.group_add_student, name='group_add_student'),
    path('manage/group_modify/delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('manage/tasks_info/', views.task_list_select, name='task_list_select'),
    path('manage/tasks_info/<int:user_id>', views.tasks_info, name = 'tasks_info'),
    path('manage/dashboards/', views.list_charts, name='dashboards'),
    path('manage/dashboards/types_errors/', views.chart_errors_types, name='types_errors'),
    path('manage/dashboards/grade_errors/', views.chart_grade_errors, name='grade_errors'),
    path('manage/dashboards/types_grade_errors/', views.chart_types_grade_errors, name='types_grade_errors'),
    path('manage/dashboards/student_dynamics/', views.chart_student_dynamics, name='student_dynamics'),
    path('manage/dashboards/errors_groups/', views.chart_group_errors, name='groups_errors'),
    path('manage/dashboards/errors_emotions/', views.chart_emotion_errors, name='emotions_errors'),
    path('manage/dashboards/errors_student_assesment/', views.chart_self_asses_errors, name='self_assesment_errors'),
    path('manage/dashboards/relation_assesment_student_assesment/', views.chart_relation_asses_sel_asses,
         name='relation_assesment_self_assesment')
]
