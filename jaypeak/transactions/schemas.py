from urllib.parse import parse_qs
import logging

from marshmallow import post_load, validates_schema, ValidationError

from ..yodlee.schemas import RegisterUserResponseMixin, \
    TransactionResponseMixin, FastlinkTokenResponseMixin, \
    LoginCobrandResponseMixin, ErrorResponseMixin

from .models import User, Transaction


class UserSchema(RegisterUserResponseMixin):

    @post_load
    def make_user(self, data):
        return User(yodlee_user_id=data['user']['id'])


class UserSessionTokenSchema(RegisterUserResponseMixin):

    @post_load
    def make_token(self, data):
        return data['user']['session']['user_session']


class TransactionSchema(TransactionResponseMixin):

    @post_load
    def make_transactions(self, data):
        transactions = []
        for transaction in data['transactions']:
            transaction = Transaction(
                amount=transaction['amount']['amount'],
                description=transaction['description']['original'],
                date=transaction['post_date'],
                account_id=transaction['account_id'],
                yodlee_transaction_id=transaction['yodlee_transaction_id'],
            )
            transactions.append(transaction)
        return transactions


class FastlinkTokenSchema(FastlinkTokenResponseMixin):

    @validates_schema
    def validate_token(self, data):
        parameters = parse_qs(data['parameters'])
        try:
            token = parameters['token'][0]
        except (IndexError, KeyError):
            raise ValidationError('Token missing from parameters')

    @post_load
    def get_token(self, data):
        parameters = parse_qs(data['parameters'])
        return parameters['token'][0]


class CobrandSessionTokenSchema(LoginCobrandResponseMixin):

    @post_load
    def get_cobrand_session_token(self, data):
        return data['session']['cob_session']

    def load(self, data, **kwargs):
        result = super(LoginCobrandResponseMixin, self).load(data)
        if result.errors:
            message = (
                'Data: {data}\n'
                'Deserialization errors: {errors}\n'
            ).format(
                data=data,
                errors=result.errors,
            )
            logging.error(message)
        return result


user_schema = UserSchema()
user_session_token_schema = UserSessionTokenSchema()
transaction_schema = TransactionSchema()
fastlink_token_schema = FastlinkTokenSchema()
cobrand_session_token_schema = CobrandSessionTokenSchema()
error_response = ErrorResponseMixin()
