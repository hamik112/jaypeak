import string
import random
import logging

from flask import abort
from requests import RequestException
from .schemas import transaction_schema, user_schema, \
    user_session_token_schema, cobrand_session_token_schema, \
    fastlink_token_schema, error_response

from .models import User

from ..extensions import yc


def generate_random_string(length):
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )
    return random_string


def get_yodlee_error_message_from_json_response(json_):
    result = error_response.load(json_)
    if result.errors:
        message = 'Json: {}'.format(json_)
        logging.error(message)
        return 'Error contacting the server'

    if result.data['error_code'] in ['Y800', 'Y801', 'Y808']:
        return result.data['error_message']
    elif result.data['error_code'] in ['Y002']:
        return result.data['error_message']

    message = 'Json: {}'.format(json_)
    logging.error(message)
    return 'Error contacting the server'


def get_yodlee_cobrand_session_token_or_400():
    try:
        response = yc.login_cobrand()
    except (RequestException, ValueError) as e:
        logging.error(e, exc_info=True)
        abort(400)

    token, errors = cobrand_session_token_schema.load(response.json())
    if errors:
        logging.error(errors)
        abort(400)

    return token


def get_yodlee_transactions_or_400(cobrand_session_token, user_session_token, params=None):  # nopep8
    try:
        response = yc.get_transactions(
            cobrand_session_token,
            user_session_token,
            params
        )
    except (RequestException, ValueError) as e:
        logging.error(e, exc_info=True)
        abort(400)

    if response.json() == {}:
        return []

    transactions, errors = transaction_schema.load(response.json())

    if errors:
        logging.error(errors)
        abort(400)

    return transactions


def get_yodlee_fastlink_token_or_400(cobrand_session_token, user_session_token):  # nopep8
    try:
        response = yc.get_fastlink_token(
            cobrand_session_token,
            user_session_token,
        )
    except (RequestException, ValueError) as e:
        logging.error(e, exc_info=True)
        abort(400)

    fastlink_token, errors = fastlink_token_schema.load(response.json())
    if errors:
        logging.error(errors)
        abort(400)

    return fastlink_token


def unregister_yodlee_user_or_400(cobrand_session_token, user_session_token):
    try:
        yc.unregister_user(
            cobrand_session_token,
            user_session_token,
        )
    except (RequestException, ValueError) as e:
        logging.error(e, exc_info=True)
        abort(400)


def login_yodlee_user(cobrand_session_token, username, password):
    response = yc.login_user(cobrand_session_token, username, password)
    user, user_errors = user_schema.load(response.json())
    token, token_errors = user_session_token_schema.load(response.json())
    if user_errors or token_errors:
        message = get_yodlee_error_message_from_json_response(response.json())
        return None, None, message

    user = User.query.filter_by(yodlee_user_id=user.yodlee_user_id).first()
    if not user:
        return None, None, 'Invalid username'

    return user, token, None


def register_yodlee_user(cobrand_session_token, username, password, email):
    response = yc.register_user(
        cobrand_session_token,
        username,
        password,
        email,
    )
    user, user_errors = user_schema.load(response.json())
    token, token_errors = user_session_token_schema.load(response.json())
    if not user_errors and not token_errors:
        return user, token, None

    message = get_yodlee_error_message_from_json_response(response.json())
    return None, None, message
