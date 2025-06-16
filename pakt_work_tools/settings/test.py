"""
Настройки для тестирования
"""

from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lingo',
        'USER': 'root',
        'PASSWORD': 'lingolingo',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'CHARSET': 'utf8mb4',
    }
}
