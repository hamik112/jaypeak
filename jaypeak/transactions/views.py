from flask import Blueprint, render_template, url_for, redirect, flash, \
    session, abort, request, jsonify
from flask.views import MethodView
from flask_login import login_required, current_user, login_user, logout_user

from ..extensions import yc, db
from .models import RecurringTransaction, User
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

            # Prevents circular imports
            from . import tasks
            tasks.sync_transactions.delay(
                session['cobrand_session_token'],
                session['user_session_token'],
                user.id,
            )
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
        user = User(email=register_form.email.data)
        db.session.add(user)
        db.session.flush()

        yodlee_user, token, error = utils.register_yodlee_user(
            session['cobrand_session_token'],
            user.username,
            register_form.password.data,
            user.email,
        )

        if not error:
            user.yodlee_user_id = yodlee_user.yodlee_user_id
            db.session.commit()
            user.save()
            session['user_session_token'] = token
            login_user(user)
            return redirect(url_for('.welcome'))

        db.session.rollback()
        flash(error, 'danger')

    return render_template(
        'transactions/register.html',
        register_form=register_form,
    )


@bp.route('/sync-transactions/status/<id>')
def sync_transactions_status(id):
    # Prevents circular imports
    from . import tasks
    task = tasks.sync_transactions.AsyncResult(id)
    return jsonify({'state': task.state})


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


@bp.route('/welcome')
def welcome():
    return render_template('transactions/welcome.html')


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


@bp.route('/welcome/sync-transactions')
def welcome_sync_transactions():
    # Prevents circular imports
    from . import tasks
    task = tasks.sync_transactions.delay(
        session['cobrand_session_token'],
        session['user_session_token'],
        current_user.id
    )
    url = url_for('.sync_transactions_status', id=task.id)
    return render_template(
        'transactions/sync_transactions.html',
        sync_transactions_status_url=url,
    )


@bp.route('/cobrand_session_token')
def cobrand_session_token():
    cobrand_session_token = utils.get_yodlee_cobrand_session_token_or_400()
    return jsonify({
        'cobrand_session_token': cobrand_session_token
    })


class SyncTransactions(MethodView):

    def get(self, user_id, task_id):
        # Prevents circular imports
        from . import tasks
        task = tasks.sync_transactions.AsyncResult(id)
        return jsonify({
            'state': task.state,
            'id': task.id,
        })

    def post(self, user_id):
        # Prevents circular imports
        from . import tasks
        task = tasks.sync_transactions.delay(
            session['cobrand_session_token'],
            session['user_session_token'],
            user_id
        )
        return jsonify({
            'state': task.state,
            'id': task.id,
        })

sync_transaction_view = SyncTransactions.as_view('sync_transactions')
bp.add_url_rule(
    '/user/<int:user_id>/sync_transactions',
    view_func=sync_transaction_view,
    methods=['POST', ]
)
bp.add_url_rule(
    '/user/<int:user_id>/sync_transactions/<task_id>',
    view_func=sync_transaction_view,
    methods=['GET', ]
)
