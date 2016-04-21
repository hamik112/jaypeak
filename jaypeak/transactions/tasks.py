from ..celery_app import create_celery_app
from . import utils
from .models import Transaction, RecurringTransaction

celery = create_celery_app()


@celery.task
def sync_transactions(cobrand_session_token, user_session_token, user_id):
    yodlee_transactions = utils.get_yodlee_transactions_or_400(
        cobrand_session_token,
        user_session_token,
    )
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
