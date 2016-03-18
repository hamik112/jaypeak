import os
from datetime import timedelta

_this_directory = os.path.dirname(os.path.abspath(__file__))


class Config(object):
    BASE_DIRECTORY = _this_directory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_REGISTERABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=25)


class TestConfig(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'U6IOODCSLXIM6GJVYPXEN3VT'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/testing'
    SECURITY_PASSWORD_HASH = 'plaintext'
    SECURITY_PASSWORD_SALT = None


class LocalConfig(Config):
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'U6IOODCSLXIM6GJVYPXEN3VT'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/local'
    SECURITY_PASSWORD_HASH = 'plaintext'
    SECURITY_PASSWORD_SALT = None


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SQLALCHEMY_DATABASE_URI = os.getenv('HEROKU_POSTGRESQL_GREEN_URL')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=25)
