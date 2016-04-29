from flask_restless import APIManager, ProcessingException

from .transactions.models import Role, User, Transaction, RecurringTransaction

from flask_login import current_user


def auth_func(*args, **kw):
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated', code=401)

api_manager = APIManager()


def configure_api_manager(app, db):
    # This was giving me problems.
    # https://github.com/jfinkels/flask-restless/issues/409
    db.app = app
    preprocessors = {
        'GET_MANY': [auth_func],
        'GET_SINGLE': [auth_func],

    }
    api_manager.init_app(
        app,
        flask_sqlalchemy_db=db,
        preprocessors=preprocessors,
    )
    api_manager.create_api(
        User,
        methods=['GET'],
        app=app,
    )
    api_manager.create_api(
        Transaction,
        methods=['GET'],
        app=app,
    )
    api_manager.create_api(
        RecurringTransaction,
        methods=['GET'],
        app=app,
    )
    api_manager.create_api(
        Role,
        methods=['GET'],
        app=app,
    )
