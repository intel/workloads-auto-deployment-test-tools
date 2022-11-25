from taas.settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'taas',
        'USER': 'postgres',
        'PASSWORD': '#1Danger0us',
        'HOST': 'db',
        'PORT': '5432',
    }
}
