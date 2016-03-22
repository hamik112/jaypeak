import os
import pytest

from jaypeak import create_app
from jaypeak.extensions import db, admin
from jaypeak.transactions.models import User


@pytest.fixture
def app():
    if os.environ.get('CONFIG') and os.environ.get('CONFIG') != 'config.CIConfig':  # nopep8
        raise RuntimeError('Invalid CONFIG environment variable')
    else:
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
    user = User(yodlee_user_id=1)
    user.save()
    return user
