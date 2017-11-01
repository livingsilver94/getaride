"""
Django settings for getaride project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from . import private_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = private_settings.key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'planner.apps.PlannerConfig',
    'cities_light',
    'leaflet',
    'users',
    # Remember: autocomplete-light must be listed before django.contrib.admin
    'dal',
    'dal_select2',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'getaride.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'getaride.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

import sys

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'testdb',
        },
    }
else:
    DATABASES = {
        'default': private_settings.database,
    }

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = 'planner:login'

LOGIN_REDIRECT_URL = 'planner:homepage'

LOGOUT_REDIRECT_URL = 'planner:homepage'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_INPUT_FORMATS = (
    '%d.%m.%Y', '%d.%m.%Y', '%d.%m.%y',  # '25.10.2006', '25.10.2006', '25.10.06'
    '%d-%m-%Y', '%d/%m/%Y', '%d/%m/%y',  # '25-10-2006', '25/10/2006', '25/10/06'
    '%d %b %Y',  # '25 Oct 2006',
    '%d %B %Y',  # '25 October 2006',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

CITIES_LIGHT_TRANSLATION_LANGUAGES = [LANGUAGE_CODE]

CITIES_LIGHT_INCLUDE_COUNTRIES = [LANGUAGE_CODE.upper()]

CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPLA', 'PPLA2', 'PPLA3']

LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (6.345, 36.0, 20.0, 47.3),
    'MIN_ZOOM': 6,
    'MAX_ZOOM': 10,
}
