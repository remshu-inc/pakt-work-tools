"""
Настройки для тестирования
"""

from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lingo',
        'USER': 'lingo',
        'PASSWORD': 'lingolingo',
        'HOST': 'mysql',
        'PORT': '3306',
        'CHARSET': 'utf8mb4',
    }
}
