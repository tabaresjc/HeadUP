# -*- coding: utf8 -*-

import os
import flask
import jinja2
import config

app = flask.Flask(__name__)

# -------------------------------------------------------------------------
# Load the app's configuration
# -------------------------------------------------------------------------
app.config.from_object('config')

# -------------------------------------------------------------------------
# Session Configuration
# -------------------------------------------------------------------------
from flask_session import Session  # noqa
Session(app)

# -------------------------------------------------------------------------
# Load celery
# -------------------------------------------------------------------------
from celery import Celery  # noqa
mq = Celery('tasks', broker=config.BROKER_URL)

# -------------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------------
from flask_sqlalchemy import SQLAlchemy  # noqa
sa = SQLAlchemy(app)

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
# Load flask mail
# -------------------------------------------------------------------------
from flask_mail import Mail  # noqa
mail = Mail(app)

# -------------------------------------------------------------------------
# Load the CSRF Protection
# -------------------------------------------------------------------------
from flask_wtf.csrf import CSRFProtect  # noqa
csrf = CSRFProtect(app)

# -------------------------------------------------------------------------
# Load the Babel extension for Internationalization
# -------------------------------------------------------------------------
from flask_babel import Babel  # noqa
babel = Babel(app)

# -------------------------------------------------------------------------
# Load the app's configuration
# -------------------------------------------------------------------------
from app.helpers import LogHelper  # noqa
logger = LogHelper(app)

# -------------------------------------------------------------------------
# Cache Configuration
# -------------------------------------------------------------------------
from app.helpers import CacheHelper  # noqa
cache = CacheHelper(app, config=config.CACHE_CONFIG)

# -------------------------------------------------------------------------
# Register modules of the application
# -------------------------------------------------------------------------
import configuration  # noqa
import helpers  # noqa
import filters  # noqa
import models  # noqa
import views  # noqa
