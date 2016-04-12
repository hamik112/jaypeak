from flask import redirect, url_for, request

import flask_admin
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, current_user
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension

from . import yodlee

bootstrap = Bootstrap()
db = SQLAlchemy()
security = Security()
login_manager = LoginManager()
toolbar = DebugToolbarExtension()


class AdminIndexView(flask_admin.AdminIndexView):

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


admin = flask_admin.Admin(
    name='jaypeak',
    template_mode='bootstrap3',
    index_view=AdminIndexView()
)

yc = yodlee.Client()
