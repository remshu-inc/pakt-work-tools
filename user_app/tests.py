"""
Тесты модуля пользователей
"""

from django.test import TestCase

from right_app.models import TblRights
from user_app.login import MyBackend
from user_app.models import TblLanguage, TblUser, TblTeacher, TblGroup


class CQLTestCase(TestCase):
    """
    Тесты модуля пользователей
    """

    def setUp(self) -> None:
        """
        Заполнение БД данными
        """
        super().setUp()
        TblLanguage.objects.create(id_language=1, language_name="Deutsche")
        TblLanguage.objects.create(id_language=2, language_name="France")

        TblUser.objects.create(id_user=1, login="root", password=MyBackend.get_hash_pass("password"),
                               language=TblLanguage.objects.get(id_language=1))
        TblTeacher.objects.create(id_teacher=1, user=TblUser.objects.get(id_user=1))

        TblGroup.objects.create(id_group=1, group_name="test_group", enrollement_date="2020-01-01", course_number=1,
                                language=TblLanguage.objects.get(id_language=1))

        TblRights.objects.create(id_right=1, name="Просмотр текстов")
        TblRights.objects.create(id_right=2, name="Загрузка текста")
        TblRights.objects.create(id_right=3, name="Удаление текстов")
        TblRights.objects.create(id_right=4, name="Изменение метаданных")
        TblRights.objects.create(id_right=5, name="Аннотирование")
        TblRights.objects.create(id_right=6, name="Суперпользователь")

    def test_login_form(self):
        """
        Проверка формы авторизации
        """
        resp = self.client.get('/login/')
        self.assertEqual(resp.status_code, 200)

    def test_login(self):
        """
        Проверка авторизации существующего пользователя
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)  # редирект на страницу с языками
        self.assertEqual(resp.headers['Location'], '/corpus/')

    def test_wrong_login(self):
        """
        Проверка авторизации с неправильными данными
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password2"})
        self.assertEqual(resp.status_code, 200)  # возвращает обратно на форму

    def test_anon_logout(self):
        """
        Проверка выхода анонима
        """
        resp = self.client.get('/logout/')
        self.assertEqual(resp.status_code, 302)  # редирект на домашнюю страницу
        self.assertEqual(resp.headers['Location'], '/')

    def test_user_logout(self):
        """
        Проверка выхода залогиненого пользователя
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/logout/')
        self.assertEqual(resp.status_code, 302)  # редирект на домашнюю страницу
        self.assertEqual(resp.headers['Location'], '/')

    def test_manage_page(self):
        """
        Проверка открытия страницы управления
        """
        resp = self.client.get('/manage/')
        self.assertEqual(resp.status_code, 302)  # редирект на страницу авторизации
        self.assertEqual(resp.headers['Location'], '/login/')

    def test_teacher_manage_page(self):
        """
        Проверка открытия страницы управления учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/manage/')
        self.assertEqual(resp.status_code, 200)

    def test_anon_manage_signup_form(self):
        """
        Проверка регистрации студентов анонимом
        """
        resp = self.client.get('/manage/signup/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/')

    def test_teacher_manage_signup_form(self):
        """
        Проверка получения формы учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/manage/signup/')
        self.assertEqual(resp.status_code, 200)

    def test_anon_manage_signup(self):
        """
        Регистрация студента анонимом
        """
        resp = self.client.post('/manage/signup/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/')

    def test_teacher_manage_signup(self):
        """
        Регистрация студента учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.post('/manage/signup/', data={"login": "user1", "password": "testpass1",
                                                         "birthdate": "2000-01-01", 'gender': "1", 'course_number': "1",
                                                         'group': "1",
                                                         "last_name": "test_stud_last", "name": "test_stud_name"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.post('/login/', data={"login": "user1", "password": "testpass1"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

    def test_anonym_change_pass_form(self):
        """
        Изменение пароля анонимом
        """
        resp = self.client.get('/manage/change_password')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/')

    def test_teacher_change_pass_form(self):
        """
        Форма изменения пароля учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.post('/manage/signup/', data={"login": "user1", "password": "testpass1",
                                                         "birthdate": "2000-01-01", 'gender': "1", 'course_number': "1",
                                                         'group': "1",
                                                         "last_name": "test_stud_last", "name": "test_stud_name"})

        resp = self.client.get('/manage/change_password')
        self.assertEqual(resp.status_code, 200)

    def test_teacher_change_pass(self):
        """
        Изменение пароля учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.post('/manage/signup/', data={"login": "user1", "password": "testpass1",
                                                         "birthdate": "2000-01-01", 'gender': "1", 'course_number': "1",
                                                         'group': "1",
                                                         "last_name": "test_stud_last", "name": "test_stud_name"})

        resp = self.client.post('/manage/change_password', data={"student": 1, "password": "123456"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/manage/')

    def test_anon_signup_teacher_form(self):
        """
        Проверка формы регистрации учителя анонимом
        """
        resp = self.client.get('/manage/signup_teacher/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/')

    def test_teacher_signup_teacher_form(self):
        """
        Проверка формы регистрации учителя учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/manage/signup_teacher/')
        self.assertEqual(resp.status_code, 200)

    def test_anon_signup_teacher(self):
        """
        Проверка регистрации учителя анонимом
        """
        resp = self.client.post('/manage/signup_teacher/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/')

    def test_teacher_signup_teacher(self):
        """
        Проверка регистрации учителя анонимом
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.post('/manage/signup_teacher/', data={"login": "user1", "password": "testpass1",
                                                                 "last_name": "test_teach_last",
                                                                 "name": "test_teach_name"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

    def test_anon_group_creation_form(self):
        """
        Проверка формы создания группы анонимом
        """
        resp = self.client.get('/manage/group_creation/')
        self.assertEqual(resp.status_code, 403)

    def test_teacher_group_creation_form(self):
        """
        Проверка формы создания группы учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/manage/group_creation/')
        self.assertEqual(resp.status_code, 200)

    def test_anon_group_creation(self):
        """
        Проверка создания группы анонимом
        """
        resp = self.client.post('/manage/group_creation/')
        self.assertEqual(resp.status_code, 403)

    def test_teacher_group_creation(self):
        """
        Проверка формы создания группы учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.post('/manage/group_creation/', data={"group_name": "test_group", "year": 2020, "course_number": 2})
        self.assertEqual(resp.status_code, 200)
