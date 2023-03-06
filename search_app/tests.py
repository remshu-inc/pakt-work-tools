"""
Тесты работы поисковых запросов.
"""
from django.test import TestCase


class CQLTestCase(TestCase):
    """
    Тесты для проверки работы языка CQL
    """

    def test_error_query(self):
        """
        Проверка работы одиночного запроса с ошибкой.
        """
        resp = self.client.post('/search', data={'corpus_search': '[error="Grammatik"]'})
        self.assertEqual(resp.status_code, 200)

    def test_error_with_grade_query(self):
        """
        Проверка работы запроса с ошибкой и уровнем
        """
        resp = self.client.post('/search', data={'corpus_search': '[error="Grammatik" & grade=1]'})
        self.assertEqual(resp.status_code, 200)
