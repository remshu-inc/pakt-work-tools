from django.urls import path
from . import views
from . import api

app_name = 'generator_app'
urlpatterns = [
    # main menu
    path("tests/menu/", views.main_menu, name="main_menu"),
    # list of created tests
    path("tests/created/", views.test_list, name="created"),
    # list of all tests
    path("tests/all-tests/", views.all_tests, name="all_tests"),
    # list of assigned tests
    path("tests/assigned/", views.assigned_tests, name="assigned_tests"),
    # generator menu
    path("tests/generator/", views.generator_settings, name="generator"),
    # test preview
    path("tests/<int:test_id>/", views.preview, name="preview"),
    # list of assigned students
    path("tests/<int:test_id>/students/", views.assigned_students, name="assigned_students"),
    # send test
    path("tests/<int:test_id>/send/", views.send_test, name="send"),
    # solve test
    path("tests/<int:test_id>/solve/", views.test_solver, name="solver"),
    # student's answers
    path("tests/<int:test_id>/<int:stud_id>/", views.view_answers, name="view_answers"),
    # student's texts names
    path("tests/api/student_texts/<int:student_id>", api.api_get_student_texts_names, name="get_student_texts_names"),
    # misc unlabelled
    path("tests/api/generate_tasks", api.api_generate_tasks, name="generate_tasks"),
    path("tests/api/create_test", api.api_create_test, name="create_test"),
    path("tests/api/delete_test", api.api_delete_test, name="delete_test"),
    path("tests/api/save_student_answer", api.api_save_student_answer, name="save_student_answer"),
    path("tests/api/save_test_results", api.api_save_test_results, name="save_test_results"),
    path("tests/api/get_all_tests_very_secret", api.api_get_all_tests_very_secret, name="get_all_tests_very_secret"),
    path("tests/api/get_text_very_secret/<int:text_id>", api.api_get_text_very_secret, name="get_text_very_secret"),
    path("tests/api/get_studs_by_test_very_secret/<int:test_id>", api.api_get_studs_by_test_very_secret, name="get_studs_by_test_very_secret"),
    path("tests/api/send_student_test", api.api_send_student_test, name="send_student_test"),
    path("tests/api/unsend_student_test", api.api_unsend_student_test, name="unsend_student_test"),
    path("tests/api/download_docx", api.api_downlad_docx, name="download_docx"),
    path("tests/api/change_task_texts", api.api_change_task_texts, name="change_task_texts"),
    path("tests/make_report", views.make_report, name="make_report"),
    path("tests/api/make_report", api.api_make_report, name="download_report"),

]