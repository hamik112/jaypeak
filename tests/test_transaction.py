import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from jaypeak.transactions.models import Transaction, RecurringTransaction
from jaypeak.transactions import utils


def test_transaction_get_or_create_from_yodlee_transactions(app, user):
    yodlee_transactions = [{
        'amount': 1.00,
        'description': 'description',
        'date': datetime.datetime.now(),
        'account_id': 1
    }]
    transactions = Transaction.get_or_create_from_yodlee_transactions(
        yodlee_transactions,
        user.id
    )
    assert len(transactions) == 1
    assert transactions[0].description == 'description'

    transactions = Transaction.get_or_create_from_yodlee_transactions(
        yodlee_transactions,
        user.id
    )

    assert len(transactions) == 1


def test_recurring_transaction_get_by_user_id(app, user):
    transaction = Transaction(
        amount=Decimal('1.00'),
        description='description',
        date=datetime.datetime.now(),
        user_id=user.id,
        account_id=1,
    )
    transaction.save()

    transaction = Transaction(
        amount=Decimal('1.00'),
        description='description',
        date=datetime.datetime.now() - relativedelta(months=1),
        user_id=user.id,
        account_id=1,
    )
    transaction.save()

    transaction = Transaction(
        amount=Decimal('2.00'),
        description='description',
        date=datetime.datetime.now() - relativedelta(months=1),
        user_id=user.id,
        account_id=1,
    )
    transaction.save()

    recurring_transactions = RecurringTransaction.get_by_user_id(user.id)
    assert len(recurring_transactions) == 1
    assert recurring_transactions[0].description == 'description'
    assert len(recurring_transactions[0].transactions) == 2


def test_get_error_message_from_json_response():
    json_response = {
        'errorCode': 'Y800',
        'errorMessage': 'Invalid value for loginName'
    }

    message = utils.get_yodlee_error_message_from_json_response(json_response)

    assert message == 'Invalid value for loginName'

    bad_json_response = {
        'errorMessage': 'Invalid value for loginName'
    }
    message = utils.get_yodlee_error_message_from_json_response(
        bad_json_response)

    assert message is None
