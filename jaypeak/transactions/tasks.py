import logging
from requests import RequestException

from ..celery_app import create_celery_app
from ..extensions import yc
from .schemas import transaction_schema
from .models import Transaction, RecurringTransaction

celery = create_celery_app()


@celery.task(bind=True)
def sync_transactions(self, cobrand_session_token, user_session_token, user_id):  # nopep8
    try:
        response = yc.get_transactions(
            cobrand_session_token,
            user_session_token,
        )
    except (RequestException, ValueError) as exc:
        logging.error(exc, exc_info=True)
        raise self.retry(countdown=30, exc=exc)

    if response.json() == {}:
        return

    yodlee_transactions, errors = transaction_schema.load(response.json())

    if errors:
        logging.error(errors)
        raise self.retry(countdown=30)

    transactions = []
    for yodlee_transaction in yodlee_transactions:
        transaction = Transaction.get_or_create_from_yodlee_transactions(  # nopep8
            yodlee_transaction, user_id
        )
        transactions.append(transaction)

    for transaction in transactions:
        if transaction.recurring_transaction_id:
            continue
        RecurringTransaction.add_or_create_by_transaction(transaction)
