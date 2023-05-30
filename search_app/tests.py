"""
Тесты работы поисковых запросов.
"""
from django.test import TestCase

from text_app.models import TblText, TblTextType, TblEmotional, TblWriteTool, TblWritePlace
from user_app.login import MyBackend
from user_app.models import TblLanguage, TblUser, TblTeacher


class CQLTestCase(TestCase):
    """
    Тесты для проверки работы языка CQL
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

        TblTextType.objects.create(id_text_type=1, text_type_name="Test text type",
                                   language=TblLanguage.objects.get(id_language=1))
        TblEmotional.objects.create(id_emotional=1, emotional_name="Test emotional")
        TblWriteTool.objects.create(id_write_tool=1, write_tool_name="Test write tool")
        TblWritePlace.objects.create(id_write_place=1, write_place_name="Test write place")
        TblText.objects.create(id_text=1, text_type=TblTextType.objects.get(id_text_type=1),
                               emotional=TblEmotional.objects.get(id_emotional=1),
                               write_tool=TblWriteTool.objects.get(id_write_tool=1),
                               write_place=TblWritePlace.objects.get(id_write_place=1),
                               header="Test text", text="text text text", create_date="2020-01-01", creation_course=2)

    def test_search_form(self):
        """
        Проверка получения формы поиска
        """
        resp = self.client.get('/search')
        self.assertEqual(resp.status_code, 200)

    def test_error_query(self):
        """
        Проверка работы одиночного запроса с ошибкой.
        """
        resp = self.client.post('/search', data={'corpus_search': '[error="Grammatik"]'})
        self.assertEqual(resp.status_code, 200)

    def test_not_error_query(self):
        """
        Проверка работы одиночного запроса с ошибкой.
        """
        resp = self.client.post('/search', data={'corpus_search': '[error!="Grammatik"]'})
        self.assertEqual(resp.status_code, 200)

    def test_word_query(self):
        """
        Проверка работы одиночного запроса со словом.
        """
        resp = self.client.post('/search', data={'corpus_search': '[word = "man"]'})
        self.assertEqual(resp.status_code, 200)

    def test_not_word_query(self):
        """
        Проверка работы одиночного запроса со словом.
        """
        resp = self.client.post('/search', data={'corpus_search': '[word != "man"]'})
        self.assertEqual(resp.status_code, 200)

    def test_pos_query(self):
        """
        Проверка работы одиночного запроса с частью речи.
        """
        resp = self.client.post('/search', data={'corpus_search': '[pos = "NOUN"]'})
        self.assertEqual(resp.status_code, 200)

    def test_not_pos_query(self):
        """
        Проверка работы одиночного запроса с частью речи.
        """
        resp = self.client.post('/search', data={'corpus_search': '[pos != "NOUN"]'})
        self.assertEqual(resp.status_code, 200)

    def test_regex_query(self):
        """
        Проверка работы одиночного запроса с частью речи.
        """
        resp = self.client.post('/search', data={'corpus_search': '[word = ".*man.*"]'})
        self.assertEqual(resp.status_code, 200)

    def test_not_regex_query(self):
        """
        Проверка работы одиночного запроса с частью речи.
        """
        resp = self.client.post('/search', data={'corpus_search': '[word != ".*man.*"]'})
        self.assertEqual(resp.status_code, 200)

    def test_error_with_grade_query(self):
        """
        Проверка работы запроса с ошибкой и уровнем
        """
        resp = self.client.post('/search', data={'corpus_search': '[error="Grammatik" & grade=1]'})
        self.assertEqual(resp.status_code, 200)

    def test_home_path(self):
        """
        Проверка получения домашней страницы
        """
        resp = self.client.get('')
        self.assertEqual(resp.status_code, 200)

    def test_cql_faq(self):
        """
        Проверка получения страницы с помощью
        """
        resp = self.client.get('/cql_faq')
        self.assertEqual(resp.status_code, 200)

    def test_tag_list(self):
        """
        Проверка получения списка тегов
        """
        resp = self.client.get('/tag_list')
        self.assertEqual(resp.status_code, 200)

    def test_search_text(self):
        """
        Проверка просмотра текста из поиска
        """
        resp = self.client.get('/search/1/')
        self.assertEqual(resp.status_code, 200)

    def test_search_unknown_text(self):
        """
        Проверка доступа к несуществующему тексту
        """
        resp = self.client.get('/search/1000/')
        self.assertEqual(resp.status_code, 404)  # должна быть страница с сообщением об отсутствии текста

    def test_search_stat_anon(self):
        """
        Проверка получения статистик анонимом
        """
        resp = self.client.get('/search/statistic')
        self.assertEqual(resp.status_code, 301)  # должен быть редирект на страницу авторизации

    def test_search_stat_teacher(self):
        """
        Получение формы статистики учителем
        """
        self.client.post('/login/', data={"login": "root", "password": "password"})
        resp = self.client.get('/search/statistic')
        self.assertEqual(resp.status_code, 200)
