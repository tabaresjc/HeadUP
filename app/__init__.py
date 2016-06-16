# -*- coding: utf8 -*-

from flask import Flask
from flask.ext.login import LoginManager, current_user
from flask_wtf.csrf import CsrfProtect
from flask.ext.babel import Babel, lazy_gettext

from werkzeug import LocalProxy, cached_property, ImmutableDict
from werkzeug.contrib.fixers import ProxyFix

from storm.locals import create_database, Store, ReferenceSet, Desc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from config import LANGUAGES
import flask
import jinja2
import os

app = Flask(__name__)

# Set the location of the templates
app.jinja_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('templates'),
])
if os.environ.get('HEROKU') is None:
    app.debug = True

# -------------------------------------------------------------------------
# Load the app's configuration
# -------------------------------------------------------------------------
app.config.from_object('config')

# -------------------------------------------------------------------------
# Load the CSRF Protection
# -------------------------------------------------------------------------
csrf = CsrfProtect()
csrf.init_app(app)

# -------------------------------------------------------------------------
# Load the Babel extension for Internationalization
# -------------------------------------------------------------------------
babel = Babel(app)


@babel.localeselector
def get_locale():
    if current_user and current_user.is_authenticated:
        return current_user.lang
    return flask.request.accept_languages.best_match(LANGUAGES.keys())


@babel.timezoneselector
def get_timezone():
    if current_user and current_user.is_authenticated:
        return current_user.timezone
    return "Asia/Tokyo"

# -------------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------------
db = SQLAlchemy(app)

# -------------------------------------------------------------------------
# Load the session controller
# -------------------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
# add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "sessions.login"
login_manager.login_message = lazy_gettext('Please log in to access this page.')

# -------------------------------------------------------------------------
# Register Views
# -------------------------------------------------------------------------
import blog.views  # noqa
import admin.views  # noqa

# register the sessions module blueprint
from app.sessions.views import mod as sessionsModule  # noqa
app.register_blueprint(sessionsModule, url_prefix='/members')

# register the Category module
from app.categories.views import CategoriesView  # noqa
CategoriesView.register(app)

# register the Post module
from app.posts.views import PostsView  # noqa
PostsView.register(app)

# register the User module
from app.users.views import UsersView  # noqa
UsersView.register(app)

# -------------------------------------------------------------------------
# Register the filters
# -------------------------------------------------------------------------
from utils import init_jinja_filters  # noqa
init_jinja_filters(app)

# -------------------------------------------------------------------------
# Application's event handlers
# -------------------------------------------------------------------------


@app.after_request
def after_request_handler(response=None):
    # close_db_connection()
    return response


@app.before_request
def before_request(response=None):
    # if flask.request.endpoint:
    #     if 'redirect_to' in flask.session and flask.request.endpoint not in ['static', 'sessions.login', 'sessions.signup', 'sessions.login_comment']:
    #         flask.session.pop('redirect_to', None)
    return response


@app.errorhandler(401)
def internal_error_401(error):
    return flask.render_template('admin/401.html', title='Error %s' % error), 401


@app.errorhandler(403)
def internal_error_403(error):
    return flask.render_template('admin/403.html', title='Error %s' % error), 403


@app.errorhandler(404)
def internal_error_404(error):
    return flask.render_template('admin/404.html', title='Error %s' % error), 404


@app.errorhandler(500)
def internal_error_500(error):
    return flask.render_template('admin/500.html', title='Error %s' % error), 500


if app.debug:
    import sys
    from storm.tracer import debug
    debug(True, stream=sys.stdout)
