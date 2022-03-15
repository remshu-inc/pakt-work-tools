from django.contrib.auth.base_user import BaseUserManager
# from django.utils.translation import ugettext_lazy as _
from hashlib import sha512

class CustomUserManager(BaseUserManager):
    
    def hash_password(self, password):
        
        salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
        hash = sha512((password+salt).encode('utf-8'))
        hash = hash.hexdigest()
        
        return hash
    
    def create_user(self, login, password, **extra_fields):
        # TODO: Проверка логина ?!
        # if not login:
            # raise ValueError(_('The Email must be set'))
        login = login
        hash = self.hash_password(password)
        
        user = self.model(login=login, password=hash, **extra_fields)
        user.save()
        
        return user
    
    def create_superuser(self, login, password):
        
        login = login
        hash = self.hash_password(password)
        
        # user = self.model(login=login, password=hash, name='Admin', last_name='AdminA', is_staff=True)
        # user.save()
        
        return None