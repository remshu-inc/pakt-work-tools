from django.contrib.auth.backends import BaseBackend
from user_app.models import TblUser
from right_app.views import check_permissions_text
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
        
        # user.permission_text = check_permissions_text(user.id_user)
            
        return user
        