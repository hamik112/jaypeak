import os
import pytest

from jaypeak import create_app
from jaypeak.extensions import db, admin, yc
from jaypeak.transactions.models import User
from jaypeak.transactions.schemas import cobrand_session_token_schema, \
    user_session_token_schema


@pytest.fixture
def app():
    if not os.environ.get('CONFIG'):
        os.environ["CONFIG"] = 'config.TestConfig'
    # http://stackoverflow.com/questions/18002750/flask-admin-blueprint-creation-during-testing
    admin._views = []
    app = create_app()
    db.app = app
    db.drop_all()
    db.create_all()
    return app


@pytest.fixture
def user(app):
    user = User(yodlee_user_id=1, email='user@example.com')
    user.save()
    return user


@pytest.fixture
def cobrand_session_token():
    response = yc.login_cobrand()
    cobrand_session_token, _ = cobrand_session_token_schema.load(response.json())  # nopep8
    return cobrand_session_token


@pytest.fixture
def user_session_token(cobrand_session_token):
    response = yc.login_user(
        cobrand_session_token=cobrand_session_token,
        username='sbMemmassover5',
        password='sbMemmassover5#123',
    )
    user_session_token, errors = user_session_token_schema.load(response.json())  # nopep8
    assert errors == {}
    return user_session_token
