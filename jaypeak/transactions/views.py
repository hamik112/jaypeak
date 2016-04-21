from flask import Blueprint, render_template, url_for, redirect, flash, \
    session, abort, request
from flask_login import login_required, current_user, login_user, logout_user

from ..extensions import yc
from .models import Transaction, RecurringTransaction, User
from .forms import LoginForm, RegisterForm
from . import utils

bp = Blueprint('transactions', __name__)


@bp.route('/')
def index():
    return render_template('transactions/index.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()

        if user:
            user, token, error = utils.login_yodlee_user(
                session['cobrand_session_token'],
                user.username,
                login_form.password.data
            )
        else:
            error = 'Email not found'

        if not error:
            login_user(user)
            session['user_session_token'] = token
            return redirect(url_for('.sync_transactions'))

        flash(error, 'danger')

    return render_template(
        'transactions/login.html',
        login_form=login_form
    )


@bp.route('/sync-transactions')
@login_required
def sync_transactions():
    yodlee_transactions = utils.get_yodlee_transactions_or_400(
        session['cobrand_session_token'],
        session['user_session_token'],
    )
    transactions = []
    for yodlee_transaction in yodlee_transactions:
        transaction = Transaction.get_or_create_from_yodlee_transactions(  # nopep8
            yodlee_transaction, current_user.id
        )
        transactions.append(transaction)

    for transaction in transactions:
        if transaction.recurring_transaction_id:
            continue
        RecurringTransaction.add_or_create_by_transaction(transaction)

    return redirect(url_for('.recurring_transactions'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = User(email=register_form.email.data)
        user.save()

        yodlee_user, token, error = utils.register_yodlee_user(
            session['cobrand_session_token'],
            user.username,
            register_form.password.data,
            user.email,
        )
        if not error:
            user.yodlee_user_id = yodlee_user.yodlee_user_id
            user.save()
            session['user_session_token'] = token
            login_user(user)
            return redirect(url_for('.welcome'))

        flash(error, 'danger')

    return render_template(
        'transactions/register.html',
        register_form=register_form,
    )


@bp.route('/logout')
@login_required
def logout():
    session.pop('user_session_token', None)
    logout_user()
    flash('You are now logged out')
    return redirect(url_for('.login'))


@bp.route('/recurring-transactions')
@login_required
def recurring_transactions():
    if request.args.get('page') is None:
        page = 1
    else:
        page = int(request.args.get('page'))
    query = RecurringTransaction.query_by_user_id(current_user.id)  # nopep8
    recurring_transactions = query.paginate(page, 5, True)
    return render_template(
        'transactions/recurring_transactions.html',
        recurring_transactions=recurring_transactions
    )


@bp.route('/recurring-transactions/<int:id>')
@login_required
def recurring_transaction(id):
    if request.args.get('page') is None:
        page = 1
    else:
        page = int(request.args.get('page'))
    recurring_transaction = RecurringTransaction.query.get_or_404(id)
    if current_user.id != recurring_transaction.user_id:
        abort(404)
    return render_template(
        'transactions/recurring_transaction.html',
        recurring_transaction=recurring_transaction,
        page=page,
    )


@bp.route('/settings')
@login_required
def settings():
    return render_template(
        'transactions/settings.html',
    )


@bp.route('/delete-user')
@login_required
def delete_user():
    utils.unregister_yodlee_user_or_400(
        session['cobrand_session_token'],
        session['user_session_token'],
    )
    current_user.delete()
    logout_user()
    flash('Your account was deleted')
    return redirect(url_for('.index'))


@bp.route('/welcome/add-accounts')
@login_required
def add_accounts():
    fastlink_token = utils.get_yodlee_fastlink_token_or_400(
        session['cobrand_session_token'],
        session['user_session_token'],
    )
    fastlink_url = yc.config['FASTLINK_URL']
    return render_template(
        'transactions/add_accounts.html',
        user_session_token=session['user_session_token'],
        fastlink_token=fastlink_token,
        fastlink_url=fastlink_url
    )


@bp.route('/welcome')
def welcome():
    return render_template('transactions/welcome.html')


@bp.route('/welcome/sync-transactions')
def sync_transactions2():
    return render_template('transactions/sync_transactions.html')
