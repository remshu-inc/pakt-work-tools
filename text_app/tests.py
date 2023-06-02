"""
Тесты модуля текстов
"""
from django.test import TestCase

from right_app.models import TblRights, TblUserRights
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

        TblRights.objects.create(id_right=1, name="view")
        TblRights.objects.create(id_right=2, name="load")
        TblRights.objects.create(id_right=3, name="delete")
        TblRights.objects.create(id_right=4, name="metadata")
        TblRights.objects.create(id_right=5, name="annotate")
        TblRights.objects.create(id_right=6, name="superuser")

        TblUser.objects.create(id_user=1, login="root", password=MyBackend.get_hash_pass("password"),
                               language=TblLanguage.objects.get(id_language=1))
        TblUser.objects.create(id_user=2, login="student1", password=MyBackend.get_hash_pass("password"),
                               language=TblLanguage.objects.get(id_language=1))
        TblTeacher.objects.create(id_teacher=1, user=TblUser.objects.get(id_user=1))
        TblStudent.objects.create(id_student=2, user=TblUser.objects.get(id_user=2), course_number=2)

        TblUserRights.objects.create(id_user_right=1, right_id=1, user_id=1)
        TblUserRights.objects.create(id_user_right=2, right_id=2, user_id=1)
        TblUserRights.objects.create(id_user_right=3, right_id=3, user_id=1)
        TblUserRights.objects.create(id_user_right=4, right_id=4, user_id=1)
        TblUserRights.objects.create(id_user_right=5, right_id=5, user_id=1)

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
        Проверка просмотра списка типов текстов учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/Deutsche/')
        self.assertEqual(resp.status_code, 200)

    def test_student_corpus_text_type(self):
        """
        Проверка просмотра списка типов текстов студентом
        """
        resp = self.client.post('/login/', data={"login": "student1", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/Deutsche/')
        self.assertEqual(resp.status_code, 200)

    def test_corpus_text_type_orders_and_others(self):
        """
        Проверка сортировок и кривого ввода типов текстов
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

    def test_teacher_corpus_text_list(self):
        """
        Проверка просмотра списка текстов учителем
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/Deutsche/Test text type/')
        self.assertEqual(resp.status_code, 200)

    def test_student_corpus_text_list(self):
        """
        Проверка просмотра списка текстов студентом
        """
        resp = self.client.post('/login/', data={"login": "student1", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/Deutsche/Test text type/')
        self.assertEqual(resp.status_code, 200)

    def test_corpus_text_list_orders_and_others(self):
        """
        Проверка сортировок и кривого ввода типов текстов
        """
        resp = self.client.post('/login/', data={"login": "root", "password": "password"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers['Location'], '/corpus/')

        resp = self.client.get('/corpus/France/123/')
        self.assertEqual(resp.status_code, 404)  # если нет ни одного типа текста, то выдает ошибку

        resp = self.client.get('/corpus/bebebe/3456/')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/3456/')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=language_name&reverse=True')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=text_type_name&reverse=True')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=ttype&reverse=True')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=header&reverse=True')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=user_id__first_name&reverse=True')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=user_id__last_name&reverse=True')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=modified_date&reverse=True')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=header')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/corpus/Deutsche/Test text type/?order_by=header&reverse=begff')
        self.assertEqual(resp.status_code, 200)
