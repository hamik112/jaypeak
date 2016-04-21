import os
from datetime import timedelta

_this_directory = os.path.dirname(os.path.abspath(__file__))


class Config(object):
    BASE_DIRECTORY = _this_directory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=25)


class TestConfig(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'U6IOODCSLXIM6GJVYPXEN3VT'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/testing'
    CELERY_BROKER_URL = None
    CELERY_RESULT_BACKEND = None
    # CELERY_ALWAYS_EAGER = True


class CIConfig(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'U6IOODCSLXIM6GJVYPXEN3VT'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost:5432/ci'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class LocalConfig(Config):
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'U6IOODCSLXIM6GJVYPXEN3VT'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/local'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('HEROKU_POSTGRESQL_GREEN_URL')
    CELERY_BROKER_URL = os.getenv('REDISTOGO_URL', '')
    CELERY_RESULT_BACKEND = os.getenv('REDISTOGO_URL', '')
