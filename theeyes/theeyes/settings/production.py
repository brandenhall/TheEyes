from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

# FIXME!
ALLOWED_HOSTS = ['theey.es', 'www.theey.es']

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'theeyes',
        'USER': 'theeyes',
        'PASSWORD': 'MuLz(sGoMQZxtL@k',
        'HOST': 'localhost',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}

WSGI_APPLICATION = 'theeyes.wsgi_production.application'

STATIC_ROOT = "/srv/static/"

MEDIA_ROOT = "/srv/media/"
