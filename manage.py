import os
import logging
import sys

from flask import current_app as app
from flask_script import Manager, prompt, prompt_pass, prompt_bool
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import jaypeak
from jaypeak import create_app
from jaypeak.transactions.models import User, Role
from jaypeak.extensions import db, yc
from jaypeak.transactions.models import Transaction, RecurringTransaction
from jaypeak.transactions.schemas import user_schema, \
    cobrand_session_token_schema

manager = Manager(create_app)


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
    print(jaypeak.transactions.utils.generate_random_string(24))


@manager.command
def create_local_db():
    engine = create_engine("postgres://localhost:5432/local")
    if not database_exists(engine.url):
        create_database(engine.url)


@manager.command
def create_test_db():
    engine = create_engine("postgres://localhost:5432/testing")
    if not database_exists(engine.url):
        create_database(engine.url)


@manager.command
def create_ci_db():
    engine = create_engine("postgresql://postgres:@localhost:5432/ci")
    if not database_exists(engine.url):
        create_database(engine.url)


@manager.command
def drop_and_create_all_tables():
    db.drop_all()
    db.create_all()


@manager.command
def seed_db():
    db.drop_all()
    db.create_all()
    role = Role(name='admin', description='admin')
    role.save()
    user = User(yodlee_user_id=10049403)
    user.roles.append(role)
    user.save()


@manager.command
def make_yodlee_user():
    email = prompt('Email')
    username = prompt('Username')
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

    response = yc.register_user(
        cobrand_session_token,
        username,
        password,
        email,
    )
    user, errors = user_schema.load(response)
    if errors:
        logging.error('response: {}'.format(response))


@manager.command
def make_user():
    yodlee_user_id = prompt('Yodlee User Id')
    user = User(yodlee_user_id=yodlee_user_id)

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
