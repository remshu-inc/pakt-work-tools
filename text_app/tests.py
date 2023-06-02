"""
Тесты модуля текстов
"""
from django.test import TestCase

from text_app.models import TblTextType
from user_app.login import MyBackend
from user_app.models import TblLanguage, TblUser, TblTeacher, TblStudent


# Create your tests here.
class TextAppTestCase(TestCase):
    """
    Тесты модуля текстов
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
        TblUser.objects.create(id_user=2, login="student1", password=MyBackend.get_hash_pass("password"),
                               language=TblLanguage.objects.get(id_language=1))
        TblTeacher.objects.create(id_teacher=1, user=TblUser.objects.get(id_user=1))
        TblStudent.objects.create(id_student=2, user=TblUser.objects.get(id_user=2), course_number=2)

        TblTextType.objects.create(id_text_type=1, text_type_name="Test text type",
                                   language=TblLanguage.objects.get(id_language=1))

    def test_anon_corpus_form(self):
        """
        Проверка просмотра списка текстов анонимом
        """
        resp = self.client.get('/corpus/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/login/')

    def test_teacher_corpus_form(self):
        """
        Проверка просмотра списка текстов учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/')
        self.assertEqual(resp.status_code, 200)

    def test_student_corpus_form(self):
        """
        Проверка просмотра списка текстов студентом
        """
        resp = self.client.post('/login/', data={"login": "student1", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/')
        self.assertEqual(resp.status_code, 200)

    def test_teacher_corpus_form_order(self):
        """
        Проверка просмотра списка текстов учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/?order_by=language_name&reverse=True')
        self.assertEqual(resp.status_code, 200)

    def test_student_corpus_form_order(self):
        """
        Проверка просмотра списка текстов студентом
        """
        resp = self.client.post('/login/', data={"login": "student1", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/?order_by=language_name&reverse=True')
        self.assertEqual(resp.status_code, 200)

    def test_wrong_lang_order(self):
        """
        Проверка обработки неправильной сортировки
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/?order_by=lang_name&reverse=True')
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get('/corpus/?order_by=language_name')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/corpus/?reverse=True')
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get('/corpus/?order_by=language_name&reverse=321')
        self.assertEqual(resp.status_code, 200)

    def test_teacher_corpus_text_type(self):
        """
        Проверка просмотра списка текстов учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/Deutsche/')
        self.assertEqual(resp.status_code, 200)

    def test_student_corpus_text_type(self):
        """
        Проверка просмотра списка текстов студентом
        """
        resp = self.client.post('/login/', data={"login": "student1", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/Deutsche/')
        self.assertEqual(resp.status_code, 200)

    def test_corpus_text_type_orders_and_others(self):
        """
        Проверка сортировок и кривого ввода
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/France/')
        self.assertEqual(resp.status_code, 404)  # если нет ни одного типа текста, то выдает ошибку

        resp = self.client.get('/corpus/bebebe/')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/?order_by=language_name&reverse=True')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/?order_by=text_type_name&reverse=True')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/corpus/Deutsche/?order_by=ttype&reverse=True')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/?order_by=text_type_name')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/corpus/Deutsche/?order_by=text_type_name&reverse=begff')
        self.assertEqual(resp.status_code, 200)

