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
# Load the app's configuration
# -------------------------------------------------------------------------
import logging  # noqa
from logging.handlers import TimedRotatingFileHandler  # noqa
log_handler = TimedRotatingFileHandler(config.LOG_PATH, 'midnight', 1)
log_handler.suffix = '%Y-%m-%d'
log_handler.setLevel(logging.DEBUG if config.DEBUG else config.INFO)
app.logger.addHandler(log_handler)

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
# Cache Configuration
# -------------------------------------------------------------------------
from app.helpers import CacheHelper  # noqa
cache = CacheHelper(app, config=config.CACHE_CONFIG)

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
# Register modules of the application
# -------------------------------------------------------------------------
import configuration  # noqa
import helpers  # noqa
import filters  # noqa
import models  # noqa
import views  # noqa
