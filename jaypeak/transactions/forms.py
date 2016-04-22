from flask_wtf import Form
from wtforms import PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.fields.html5 import EmailField

from .models import User


class LoginForm(Form):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class RegisterForm(Form):
    email = EmailField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )

    def validate_email(self, field):
        user = User.get_by_email(field.data)
        if user:
            raise ValidationError('Email address already in use')
