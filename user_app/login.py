from django.contrib.auth.backends import BaseBackend
from user_app.models import TblUser, TblTeacher
from hashlib import sha512


class MyBackend(BaseBackend):

    @staticmethod
    def authenticate(login=None, password=None):

        m_hash = MyBackend.get_hash_pass(password)
        try:
            user = TblUser.objects.get(login=login, password=m_hash)
        except:
            return None
            
        return user

    @staticmethod
    def get_hash_pass(password=None):
        """
        Получение шифрованной версии пароля. Используется также и в тестах.
        """
        salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
        m_hash = sha512((password+salt).encode('utf-8'))
        return m_hash.hexdigest()
