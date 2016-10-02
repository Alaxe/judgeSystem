"""
Django settings for judgeSystem project.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from kombu import Exchange, Queue

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secretsecretsecretsecretsecretsecretsecretsecretse'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = False

SITE_HOST = 'https://judgesystem.tk'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'judgesystem.tk', 
    'www.judgesystem.tk']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kombu.transport.django',
    'bootstrap3',
    'bootstrap_pagination',
    'markdown_deux',
    'djcelery',
    'taggit',
    'taggit_templatetags2',
    'judge',
    'captcha',
    'users',
    'blog',
    'media_manager',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/judgeSystem/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'judgeSystem.context_processors.base_url',
                'users.context_processors.base_url',
            ],
        },
    },
]

ROOT_URLCONF = 'judgeSystem.urls'

WSGI_APPLICATION = 'judgeSystem.wsgi.application'

BASE_TEMPLATE = 'judgeSystem/base.html'
BASE_NAVBAR = 'judgeSystem/navbar.html'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '', #uses default port
    },
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': 'localDB',
#    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Sofia'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATICFILES_DIRS = ['judgeSystem/static/']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR + '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

ADMINS = [('default', EMAIL_HOST_USER)]

LOGIN_URL = '/account/login/'
JUDGE_COMPILE_TL = 3

TAGGIT_CASE_INSENSITIVE = True

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

