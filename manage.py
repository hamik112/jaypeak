import os
import logging
import sys

from flask import current_app as app
from flask_script import Manager, prompt, prompt_pass, prompt_bool
from flask_migrate import MigrateCommand

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from config import TestConfig, CIConfig, LocalConfig, ProductionConfig
from jaypeak import create_app
from jaypeak.transactions.models import User, Role
from jaypeak.extensions import db, yc
from jaypeak.transactions.models import Transaction, RecurringTransaction
from jaypeak.transactions.schemas import user_schema, \
    cobrand_session_token_schema

manager = Manager(create_app)

manager.add_command('db', MigrateCommand)


@manager.command
def runserver(port=5000):
    app.run(port=int(port))


@manager.shell
def make_shell_context():
    return dict(
        app=app, db=db, Transaction=Transaction, User=User,
        RecurringTransaction=RecurringTransaction, Role=Role
    )


@manager.command
def generate_secret_key():
    from jaypeak.transactions import utils
    print(utils.generate_random_string(24))


@manager.command
def create_local_db():
    engine = create_engine(LocalConfig.SQLALCHEMY_DATABASE_URI)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    engine.execute('create extension if not exists fuzzystrmatch')


@manager.command
def create_test_db():
    engine = create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    engine.execute('create extension if not exists fuzzystrmatch')


@manager.command
def create_ci_db():
    engine = create_engine(CIConfig.SQLALCHEMY_DATABASE_URI)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    engine.execute('create extension if not exists fuzzystrmatch')


@manager.command
def update_production_db():
    engine = create_engine(ProductionConfig.SQLALCHEMY_DATABASE_URI)
    engine.execute('create extension if not exists fuzzystrmatch')


@manager.command
def drop_and_create_all_tables():
    db.drop_all()
    db.create_all()


@manager.command
def seed():
    db.drop_all()
    db.create_all()
    role = Role(name='admin', description='admin')
    role.save()
    # Username:sbMemmassover2 Password: sbMemmassover2#123
    user = User(
        email='user@example.com',
        _username='sbMemmassover2',
        yodlee_user_id=10049404,
    )
    user.roles.append(role)
    user.save()


@manager.command
def make_yodlee_user():
    email = prompt('Email')
    password = prompt_pass('Password')
    password_confirm = prompt_pass('Confirm Password')

    if password != password_confirm:
        logging.error('Passwords not equal')
        sys.exit()

    response = yc.get_cobrand_login()
    cobrand_session_token, errors = cobrand_session_token_schema.load(
        response.json())
    if errors:
        sys.exit()

    user = User(email=email)
    user.save()

    response = yc.register_user(
        cobrand_session_token,
        user.username,
        password,
        email,
    )
    yodlee_user, errors = user_schema.load(response)
    if errors:
        logging.error('response: {}'.format(response))

    user.yodlee_user_id = yodlee_user.yodlee_user_id
    user.save()


@manager.command
def make_user():
    yodlee_user_id = prompt('Yodlee User Id')
    email = prompt('Email')
    _username = prompt('Username [optional]')

    user = User(
        yodlee_user_id=yodlee_user_id,
        email=email,
        _username=_username,
    )

    if prompt_bool('Admin'):
        role = Role.query.filter_by(name='admin').first()
        user.roles.append(role)

    user.save()


@manager.command
def make_role():
    name = prompt('Name')
    description = prompt('Description', default=name)
    role = Role(name=name, description=description)
    role.save()


if __name__ == '__main__':
    if os.environ.get('CONFIG') is None:
        os.environ['CONFIG'] = 'config.LocalConfig'

    manager.run()
