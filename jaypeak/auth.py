from flask import jsonify, request
from flask_jwt import JWT, jwt_required
from .transactions.models import User
from .transactions import utils

jwt = JWT()


@jwt.authentication_handler
def authentication_handler(email, password):
    cobrand_session_token = request.headers.get('cobrand-session-token')
    if not cobrand_session_token:
        return None

    user = User.query.filter_by(email=email).first()
    if not user:
        return None

    user, token, error = utils.login_yodlee_user(
        cobrand_session_token,
        user.username,
        password
    )

    if not user:
        return None
    return user


@jwt.identity_handler
def identity_handler(payload):
    user = User.query.get(id=payload['identity'])
    return user


@jwt.auth_response_handler
def auth_response_handler(access_token, identity):
    return jsonify({
        'access_token': access_token.decode('utf-8'),
        'user_id': identity.id
    })


@jwt_required()
def authentication_preprocessor(**kw):
    pass
