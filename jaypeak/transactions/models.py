from flask_login import UserMixin
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

    @classmethod
    def get_or_create_from_yodlee_transactions(cls, yodlee_transactions, user_id):  # nopep8
        transactions = []
        for yodlee_transaction in yodlee_transactions:
            transaction = cls.query.filter_by(
                user_id=user_id,
                yodlee_transaction_id=yodlee_transaction.yodlee_transaction_id
            ).first()
            if transaction:
                transactions.append(transaction)
                continue
            yodlee_transaction.user_id = user_id
            db.session.add(yodlee_transaction)
            transactions.append(yodlee_transaction)

        db.session.commit()
        return transactions

    def save(self):
        db.session.add(self)
        db.session.commit()


class RecurringTransaction(object):

    def __init__(self, amount, description, transactions):
        self.amount = amount
        self.description = description
        self.transactions = transactions

    @classmethod
    def get_by_user_id(cls, user_id):
        rows = db.session.query(
            Transaction.amount, Transaction.description
        ).distinct().all()
        recurring_transactions = []
        for amount, description in rows:
            transactions = Transaction.query.filter_by(
                amount=amount, description=description, user_id=user_id
            ).all()

            if len(transactions) < 2:
                continue
            recurring_transaction = RecurringTransaction(
                amount,
                description,
                transactions
            )
            recurring_transactions.append(recurring_transaction)
        return recurring_transactions
