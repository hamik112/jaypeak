import sys
import logging
import os

from flask import Flask, session
from flask_security import SQLAlchemyUserDatastore

from .extensions import bootstrap, db, security, admin, login_manager, yc, \
    toolbar, migrate
from . import transactions
from jaypeak.transactions import utils
from .transactions.admin import configure_transactions_admin
from .transactions.models import User, Role, AnonymousUser
from .yodlee import ProductionConfig, SandboxConfig


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['CONFIG'])
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)
    app.register_blueprint(transactions.bp)

    app.before_request(set_cobrand_session_token)

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    bootstrap.init_app(app)
    db.init_app(app)
    admin._views = []
    admin.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'transactions.index'
    login_manager.anonymous_user = AnonymousUser
    migrate.init_app(app, db)

    toolbar.init_app(app)

    configure_transactions_admin(app, db)

    if os.environ['CONFIG'] == 'config.ProductionConfig':
        yc.config.from_object(ProductionConfig)
    else:
        yc.config.from_object(SandboxConfig)

        def register_user(*args):
            raise Exception('Disabled in SandboxConfig')

        yc.register_user = register_user

    return app


def set_cobrand_session_token():
    cobrand_session_token = utils.get_yodlee_cobrand_session_token_or_400()
    session['cobrand_session_token'] = cobrand_session_token
