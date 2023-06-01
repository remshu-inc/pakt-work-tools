"""
Тесты модуля пользователей
"""

from django.test import TestCase

from user_app.login import MyBackend
from user_app.models import TblLanguage, TblUser, TblTeacher


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

        TblUser.objects.create(id_user=1, login="root", password=MyBackend.get_hash_pass("password"), language=TblLanguage.objects.get(id_language=1))
        TblTeacher.objects.create(id_teacher=1, user=TblUser.objects.get(id_user=1))

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

    def test_user_logout(self):
        """
        Проверка выхода залогиненого пользователя
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get('/logout/')
        self.assertEqual(resp.status_code, 302)  # редирект на домашнюю страницу

    def test_manage_page(self):
        """
        Проверка открытия страницы управления
        """
        resp = self.client.get('/manage/')
        self.assertEqual(resp.status_code, 302)  # редирект на страницу авторизации

    def test_teacher_manage_page(self):
        """
        Проверка открытия страницы управления учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get('/manage/')
        self.assertEqual(resp.status_code, 200)
