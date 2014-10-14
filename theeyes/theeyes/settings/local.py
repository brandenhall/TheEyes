from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'theeyes',
        'USER': 'theeyes',
        'PASSWORD': 'dbmaster',
        'HOST': 'localhost',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}
