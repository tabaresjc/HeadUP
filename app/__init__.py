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
from app.helpers import CacheHelper  # noqa
cache = CacheHelper(app, config=config.CACHE_CONFIG)

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
# Register modules of the application
# -------------------------------------------------------------------------
import configuration  # noqa
import helpers  # noqa
import filters  # noqa
import models  # noqa
import views  # noqa
