from .base import *

DEBUG = False

ADMINS = (
    ('admin', 'test@test.com'),
)

# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['blogproject.com', 'www.blogproject.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blog',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
