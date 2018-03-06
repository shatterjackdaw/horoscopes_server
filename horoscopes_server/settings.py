# -*- coding:utf-8 -*-
import os
import msgpack
import pymongo

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = msgpack.load(open(os.path.join(os.path.dirname(__file__), 'data.bin')))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hoct8m*$*#4%149p2^jt$#06cmn$rwl4bt5@jxw72lnuw^+x$^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'horoscopes',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'horoscopes_server.middlewares.ElapseMiddleware',       # 访问日志记录
    'horoscopes_server.middlewares.ExceptionMiddleware',    # 错误日志记录
]

ROOT_URLCONF = 'horoscopes_server.urls'

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

WSGI_APPLICATION = 'horoscopes_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'


# =============================logging configure===============================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'filesystem': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'MIDNIGHT',
            'formatter': 'simple',
            'filename': os.path.join(BASE_DIR, 'logs/elapse.log')
        },
        'except_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'MIDNIGHT',
            'formatter': 'simple',
            'filename': os.path.join(BASE_DIR, 'logs/exception.log')
        }
    },
    'loggers': {
        'elapse_log': {  # 访问日志
            'handlers': ['filesystem'],
            'level': 'INFO',
        },
        'except_log': {  # 异常捕获日志
            'handlers': ['except_handler'],
            'level': 'INFO',
        }
    }
}


# =============================mongo configure===============================
MONGO_CONFIG = {
    'CONN_ADDR1': '127.0.0.1:27017',
    'CONN_ADDR2': None,

    'username': None,
    'password': None,
}


def get_mongo_conf(conf=None):
    _conf = conf or MONGO_CONFIG
    _h1, _h2 = _conf.get('CONN_ADDR1'), _conf.get('CONN_ADDR2')
    _mg_user, _mg_pass = _conf.get('username'), _conf.get('password')

    _host_list = []
    if _h1:
        _host_list.append(_h1)
    if _h2:
        _host_list.append(_h2)

    if _host_list:
        mongo = pymongo.MongoClient(_host_list, replicaSet=_conf.get('REPLICAT_SET'))
        if _mg_user and _mg_pass:
            mongo.admin.authenticate(_mg_user, _mg_pass)
    else:
        mongo = pymongo.MongoClient('127.0.0.1', 27017, connect=False, socketKeepAlive=True)
    return mongo

MONGO = get_mongo_conf(MONGO_CONFIG)

HOROSCOPES_DB = MONGO['horoscopes_db']


def reload_static_compatibility():
    new_compatibility = {}
    for _id, data in STATIC['Compatibility'].iteritems():
        new_compatibility.setdefault(data['zodiac_man'], {})
        new_data = {}
        for key, value in data.iteritems():
            new_data[key] = value

        new_compatibility[data['zodiac_man']][data['zodiac_woman']] = new_data

    STATIC['Compatibility'] = new_compatibility

reload_static_compatibility()
