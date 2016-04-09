from sqlalchemy import func

from flask_login import UserMixin, AnonymousUserMixin
from flask_security import RoleMixin

from ..extensions import db, login_manager

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def save(self):
        db.session.add(self)
        db.session.commit()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    yodlee_user_id = db.Column(db.Integer)

    transactions = db.relationship(
        'Transaction',
        backref='user',
        lazy='dynamic',
    )
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def has_role(self, role):
        return role in self.roles

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.id


class AnonymousUser(AnonymousUserMixin):
    def has_role(self, role):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    account_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    yodlee_transaction_id = db.Column(db.Integer, nullable=False)
    recurring_transaction_id = db.Column(db.ForeignKey('recurring_transaction.id'))  # nopep8

    @classmethod
    def get_or_create_from_yodlee_transactions(cls, yodlee_transaction, user_id):  # nopep8
        transaction = cls.query.filter_by(
            user_id=user_id,
            yodlee_transaction_id=yodlee_transaction.yodlee_transaction_id
        ).first()
        if transaction:
            return transaction

        yodlee_transaction.user_id = user_id
        yodlee_transaction.save()
        return yodlee_transaction

    def save(self):
        db.session.add(self)
        db.session.commit()


class RecurringTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transactions = db.relationship(
        'Transaction',
        backref='recurring_transaction',
        lazy='dynamic',
    )

    @classmethod
    def add_or_create_by_transaction(cls, transaction):
        recurring_transaction = RecurringTransaction.query.join(
            Transaction
        ).filter(
            func.levenshtein(Transaction.description, transaction.description) < 10,  # nopep8
            Transaction.amount == transaction.amount,
            Transaction.user_id == transaction.user_id,
        ).first()
        if not recurring_transaction:
            recurring_transaction = RecurringTransaction()

        recurring_transaction.transactions.append(transaction)
        recurring_transaction.save()
        return recurring_transaction

    @classmethod
    def get_by_user_id(self, user_id):
        return RecurringTransaction.query.join(
            Transaction
        ).filter(
            Transaction.user_id == user_id
        ).group_by(
            RecurringTransaction
        ).having(
            func.count(Transaction.id) > 1
        ).all()

    @property
    def description(self):
        return self.transactions[-1].description

    @property
    def amount(self):
        return self.transactions[-1].amount

    @property
    def date(self):
        return self.transactions[-1].date

    @property
    def user_id(self):
        return self.transactions[-1].user_id

    def save(self):
        db.session.add(self)
        db.session.commit()
