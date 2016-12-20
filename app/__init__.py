# -*- coding: utf8 -*-

from flask import Flask
import flask
import jinja2
import os
import config

app = Flask(__name__)

# -------------------------------------------------------------------------
# Load the app's configuration
# -------------------------------------------------------------------------
app.config.from_object('config')

# -------------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------------
from flask_sqlalchemy import SQLAlchemy  # noqa
db = SQLAlchemy(app)

# -------------------------------------------------------------------------
# Cache Configuration
# -------------------------------------------------------------------------
from app.utils.cache import CacheBase  # noqa
cache = CacheBase(app, config=config.CACHE_CONFIG)

# -------------------------------------------------------------------------
# Load the CSRF Protection
# -------------------------------------------------------------------------
from flask_wtf.csrf import CsrfProtect  # noqa
csrf = CsrfProtect(app)

# -------------------------------------------------------------------------
# Load the Babel extension for Internationalization
# -------------------------------------------------------------------------
from flask_babel import Babel  # noqa
babel = Babel(app)

# -------------------------------------------------------------------------
# Widget Configuration
# -------------------------------------------------------------------------
from flask_widgets import Widgets  # noqa
widgets = Widgets(app)

# -------------------------------------------------------------------------
# Load the session controller
# -------------------------------------------------------------------------
from flask_login import LoginManager  # noqa
login_manager = LoginManager(app)

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
    from flask_login import current_user
    if current_user and current_user.is_authenticated:
        return current_user.lang
    return flask.request.accept_languages.best_match(config.LANGUAGES.keys())


@babel.timezoneselector
def get_timezone():
    from flask_login import current_user
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
