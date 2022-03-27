from django.contrib.auth.backends import BaseBackend
from user_app.models import TblUser, TblTeacher
from hashlib import sha512


class MyBackend(BaseBackend):
    def authenticate(login=None, password=None):
        
        salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
        hash = sha512((password+salt).encode('utf-8'))
        hash = hash.hexdigest()
        
        try:
            user = TblUser.objects.get(login=login, password=hash)
        except:
            return None
            
        return user
        