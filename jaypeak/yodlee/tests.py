from datetime import datetime
import os

import pytest
from dateutil.relativedelta import relativedelta

from . import client, SandboxConfig, ProductionConfig
from jaypeak.yodlee.schemas import LoginCobrandResponseMixin, \
    LoginUserResponseMixin, FastlinkTokenResponseMixin, \
    TransactionResponseMixin, ErrorResponseMixin, RegisterUserResponseMixin


@pytest.fixture
def yc():
    yc = client.Client()
    yc.config.from_object(SandboxConfig)
    return yc


@pytest.fixture
def cobrand_session_token(yc):
    response = yc.login_cobrand()
    data, errors = LoginCobrandResponseMixin().load(response.json())
    assert errors == {}
    assert isinstance(data['session']['cob_session'], str)
    return data['session']['cob_session']


@pytest.fixture
def user_session_token(yc, cobrand_session_token):
    response = yc.login_user(
        cobrand_session_token=cobrand_session_token,
        username='sbMemmassover5',
        password='sbMemmassover5#123',
    )
    data, errors = LoginUserResponseMixin().load(response.json())
    assert errors == {}
    assert isinstance(data['user']['session']['user_session'], str)
    return data['user']['session']['user_session']


def test_get_user_session_token_with_bad_credentials(yc, cobrand_session_token):  # nopep8
    response = yc.login_user(
        cobrand_session_token=cobrand_session_token,
        username='sbMemmassover5',
        password='wrong',
    )
    assert response.status_code == 401

    data, errors = LoginUserResponseMixin().load(response.json())
    assert errors != {}

    data, errors = ErrorResponseMixin().load(response.json())
    assert errors == {}
    assert data['error_code'] == 'Y002'


def test_get_fastlink_token(yc, cobrand_session_token, user_session_token):
    response = yc.get_fastlink_token(cobrand_session_token, user_session_token)  # nopep8
    assert response.status_code == 200

    data, errors = FastlinkTokenResponseMixin().load(response.json())
    assert errors == {}
    assert isinstance(data['parameters'], str)


def test_get_transactions(yc, cobrand_session_token, user_session_token):
    from_date = datetime.now() - relativedelta(years=3)
    to_date = datetime.now()
    params = {
        'fromDate': from_date.strftime('%Y-%m-%d'),
        'toDate': to_date.strftime('%Y-%m-%d'),
    }
    response = yc.get_transactions(
        cobrand_session_token,
        user_session_token,
        params
    )
    assert response.status_code == 200

    data, errors = TransactionResponseMixin().load(response.json())
    assert len(data['transactions']) == 90


@pytest.mark.skipif(os.environ.get('CONFIG') != 'config.ProductionConfig',
                    reason='User creation/deletion is behind whitelisted ips')
def test_register_and_unregister_user_integration(cobrand_session_token):
    yc = client.Client()
    yc.config.from_object(ProductionConfig)
    username = 'username123'
    password = 'TEST@123'
    email = 'username123@gmail.org'
    response = yc.register_user(
        cobrand_session_token,
        username,
        password,
        email
    )
    assert response.status_code == 200

    data, errors = RegisterUserResponseMixin().load(response.json())
    assert errors != {}

    user_session_token = data['user']['session']['user_session']
    response = yc.unregister_user(cobrand_session_token, user_session_token)

    assert response.status_code == 204
