# -*- coding: utf8 -*-

from flask import Flask
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CsrfProtect
from flask_babel import Babel, lazy_gettext
from flask_assets import Environment, Bundle

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from config import LANGUAGES
import flask
import jinja2
import os

app = Flask(__name__)

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

# -------------------------------------------------------------------------
# Load Flask Assets
# -------------------------------------------------------------------------
assets = Environment(app)
assets.from_yaml('schema/assets.yml')
assets.auto_build = False

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
# Register Controllers & Models
# -------------------------------------------------------------------------
import models  # noqa
import main  # noqa
import admin  # noqa

# -------------------------------------------------------------------------
# Register the filters
# -------------------------------------------------------------------------
from utils import init_jinja_filters  # noqa
init_jinja_filters(app)

# -------------------------------------------------------------------------
# JSON Encoder
# -------------------------------------------------------------------------
from utils.response import CustomJSONEncoder  # noqa
app.json_encoder = CustomJSONEncoder

# -------------------------------------------------------------------------
# Application's event handlers
# -------------------------------------------------------------------------


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


@app.errorhandler(401)
def internal_error_401(error):
    return flask.render_template('main/common/401.html', title=error), 401


@app.errorhandler(403)
def internal_error_403(error):
    return flask.render_template('main/common/403.html', title=error), 403


@app.errorhandler(404)
def internal_error_404(error):
    return flask.render_template('main/common/404.html', title=error), 404


@app.errorhandler(500)
def internal_error_500(error):
    return flask.render_template('main/common/500.html', title=error), 500
