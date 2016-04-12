from datetime import datetime

from dateutil.relativedelta import relativedelta

from .models import Transaction, RecurringTransaction, User



def test_add_or_create_by_transaction(app, user):
    transaction1 = Transaction(
        date=datetime.now(),
        description='ADY*Spotify 222594292088-646-8375380  NY',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1,
    )
    transaction1.save()
    RecurringTransaction.add_or_create_by_transaction(transaction1)

    transaction2 = Transaction(
        date=datetime.now() - relativedelta(months=1),
        description='ADY*Spotify 195928071081-646-8375380  NY',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1,
    )
    transaction2.save()

    RecurringTransaction.add_or_create_by_transaction(transaction2)
    assert transaction1.recurring_transaction_id == transaction2.recurring_transaction_id  # nopep8
    assert len(RecurringTransaction.query.all()) == 1

    transaction3 = Transaction(
        date=datetime.now() - relativedelta(months=1),
        description='A Spotty Description',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1,
    )

    transaction3.save()
    RecurringTransaction.add_or_create_by_transaction(transaction3)
    assert transaction1.recurring_transaction_id != transaction3.recurring_transaction_id  # nopep8
    assert len(RecurringTransaction.query.all()) == 2


def test_get_or_create_from_yodlee_transaction(app, user):
    yodlee_transaction = Transaction(
        date=datetime.now(),
        description='Description',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1
    )
    transaction = Transaction.get_or_create_from_yodlee_transactions(
        yodlee_transaction,
        user_id=user.id
    )
    assert len(Transaction.query.all()) == 1

    yodlee_transaction = Transaction(
        date=datetime.now(),
        description='Description',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1
    )

    transaction = Transaction.get_or_create_from_yodlee_transactions(
        yodlee_transaction,
        user_id=user.id
    )

    assert len(Transaction.query.all()) == 1


def test_get_by_user_id(app, user):
    transaction1 = Transaction(
        date=datetime.now(),
        description='ADY*Spotify 222594292088-646-8375380  NY',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1,
    )
    transaction1.save()
    RecurringTransaction.add_or_create_by_transaction(transaction1)

    query = RecurringTransaction.query_by_user_id(user.id)
    assert len(query.all()) == 0

    transaction2 = Transaction(
        date=datetime.now() - relativedelta(months=1),
        description='ADY*Spotify 195928071081-646-8375380  NY',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1,
    )
    transaction2.save()

    RecurringTransaction.add_or_create_by_transaction(transaction2)
    query = RecurringTransaction.query_by_user_id(user.id)
    assert len(query.all()) == 1


def test_user_delete_cascade(app, user):
    transaction = Transaction(
        date=datetime.now(),
        description='ADY*Spotify 222594292088-646-8375380  NY',
        account_id=1,
        amount='9.99',
        user_id=user.id,
        yodlee_transaction_id=1,
    )
    transaction.save()

    RecurringTransaction.add_or_create_by_transaction(transaction)

    user.delete()
    assert len(User.query.all()) == 0
    assert len(Transaction.query.all()) == 0
    assert len(RecurringTransaction.query.all()) == 0


