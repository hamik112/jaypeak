from flask import Blueprint, render_template, url_for, redirect, flash, session
from flask_login import login_required, current_user, login_user, logout_user

from ..extensions import yc
from .models import Transaction, RecurringTransaction
from .forms import LoginForm, RegisterForm
from . import utils

bp = Blueprint('transactions', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user, token, error = utils.login_yodlee_user(
            session['cobrand_session_token'],
            login_form.username.data,
            login_form.password.data
        )

        if not error:
            login_user(user)
            session['user_session_token'] = token
            return redirect(url_for('.recurring_transactions'))

        flash(error, 'danger')

    return render_template(
        'transactions/login.html',
        login_form=login_form
    )


@bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user, token, error = utils.register_yodlee_user(
            session['cobrand_session_token'],
            register_form.username.data,
            register_form.password.data,
            register_form.email.data,
        )
        if not error:
            user.save()
            session['user_session_token'] = token
            login_user(user)
            return redirect(url_for('.recurring_transactions'))

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


@bp.route('/')
@bp.route('/recurring-transactions')
@login_required
def recurring_transactions():
    yodlee_transactions = utils.get_yodlee_transactions_or_400(
        session['cobrand_session_token'],
        session['user_session_token'],
    )

    Transaction.get_or_create_from_yodlee_transactions(
        yodlee_transactions,
        current_user.id
    )
    recurring_transactions = RecurringTransaction.get_by_user_id(
        current_user.id
    )
    return render_template(
        'transactions/recurring_transactions.html',
        recurring_transactions=recurring_transactions
    )


@bp.route('/fastlink')
@login_required
def fastlink():
    fastlink_token = utils.get_yodlee_fastlink_token_or_400(
        session['cobrand_session_token'],
        session['user_session_token'],
    )
    fastlink_url = yc.config['FASTLINK_URL']
    return render_template(
        'transactions/fastlink.html',
        user_session_token=session['user_session_token'],
        fastlink_token=fastlink_token,
        fastlink_url=fastlink_url
    )
