# Sample production settings, change as needed

from OIPA.base_settings import *

DEBUG = True

SECRET_KEY = '__DEV_SECRET_KEY__'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'oipa',
        'USER': 'oipa',
        'PASSWORD': 'oipa',
        'HOST': '127.0.0.1',
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
    'parser': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, 'static_served/')

# Additional locations of static files
STATICFILES_DIRS = (
     os.path.join(BASE_DIR, 'static/'),
)

FIXTURE_DIRS = (
     os.path.join(BASE_DIR, '../fixtures'),
)


try:
    from local_settings import *
except ImportError:
    pass
