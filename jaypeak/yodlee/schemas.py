from marshmallow import Schema, fields


class CobrandSession(Schema):
    cob_session = fields.String(load_from='cobSession', required=True)


class LoginCobrandResponseMixin(Schema):
    session = fields.Nested(CobrandSession, required=True)


class UserSession(Schema):
    user_session = fields.String(load_from='userSession', required=True)


class User(Schema):
    id = fields.Integer(required=True)
    session = fields.Nested(UserSession, required=True)


class LoginUserResponseMixin(Schema):
    user = fields.Nested(User, required=True)


class Amount(Schema):
    amount = fields.Decimal(places=2)


class Description(Schema):
    original = fields.String(required=True)


class Transaction(Schema):
    amount = fields.Nested(Amount, required=True)
    description = fields.Nested(Description, required=True)
    post_date = fields.DateTime(load_from='postDate', required=True)
    account_id = fields.Integer(load_from='accountId', required=True)
    yodlee_transaction_id = fields.Integer(load_from='id', required=True)


class TransactionResponseMixin(Schema):
    transactions = fields.List(
        fields.Nested(Transaction),
        load_from='transaction',
        required=True
    )


class FastlinkTokenResponseMixin(Schema):
    parameters = fields.String(required=True)


class RegisterUserResponseMixin(Schema):
    user = fields.Nested(User, required=True)


class ErrorResponseMixin(Schema):
    error_code = fields.String(required=True, load_from='errorCode')
    error_message = fields.String(required=True, load_from='errorMessage')
