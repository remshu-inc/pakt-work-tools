"""
Проверка функционала приложения right_app
"""

from django.test import TestCase

from right_app.models import TblUserRights, TblRights
from right_app.views import check_permissions_show_text, check_is_superuser, check_permissions_new_text, \
    check_permissions_delete_text, check_permissions_edit_text, check_permissions_work_with_annotations
from user_app.login import MyBackend
from user_app.models import TblLanguage, TblUser


# Create your tests here.
class CQLTestCase(TestCase):
    """
    Проверка функционала приложения right_app
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
        TblUser.objects.create(id_user=2, login="user", password=MyBackend.get_hash_pass("password"),
                               language=TblLanguage.objects.get(id_language=1))
        TblUserRights.objects.create(id_user_right=1, right_id=1, user_id=1)
        TblUserRights.objects.create(id_user_right=2, right_id=2, user_id=1)
        TblUserRights.objects.create(id_user_right=3, right_id=3, user_id=1)
        TblUserRights.objects.create(id_user_right=4, right_id=4, user_id=1)
        TblUserRights.objects.create(id_user_right=5, right_id=5, user_id=1)
        TblUserRights.objects.create(id_user_right=6, right_id=6, user_id=1)

    def test_check_permissions_show_text(self):
        """
        Проверка функции проверки прав на текст
        """
        self.assertTrue(check_permissions_show_text(1))
        self.assertFalse(check_permissions_show_text(2))
        self.assertFalse(check_permissions_show_text(10))

    def test_check_is_superuser(self):
        """
        Проверка суперпользователя
        """
        self.assertTrue(check_is_superuser(1))
        self.assertFalse(check_is_superuser(2))
        self.assertFalse(check_is_superuser(10))

    def test_check_permissions_new_text(self):
        """
        Проверка прав на создание текста
        """
        self.assertTrue(check_permissions_new_text(1))
        self.assertFalse(check_permissions_new_text(2))
        self.assertFalse(check_permissions_new_text(10))

    def test_check_permissions_delete_text(self):
        """
        Проверка прав на удаление текста
        """
        self.assertTrue(check_permissions_delete_text(1))
        self.assertFalse(check_permissions_delete_text(2))
        self.assertFalse(check_permissions_delete_text(10))

    def test_check_permissions_edit_text(self):
        """
        Проверка прав на редактирование текста
        """
        self.assertTrue(check_permissions_edit_text(1))
        self.assertFalse(check_permissions_edit_text(2))
        self.assertFalse(check_permissions_edit_text(10))

    def test_check_permissions_work_with_annotations(self):
        """
        Проверка прав на аннотирование текста
        """
        self.assertTrue(check_permissions_work_with_annotations(1))
        self.assertFalse(check_permissions_work_with_annotations(2))
        self.assertFalse(check_permissions_work_with_annotations(10))
