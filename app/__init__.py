# -*- coding: utf8 -*-

from flask import Flask
import flask
import jinja2
import os
import config
import logging

app = Flask(__name__)

# -------------------------------------------------------------------------
# Load the app's configuration
# -------------------------------------------------------------------------
app.config.from_object('config')

# -------------------------------------------------------------------------
# Load celery
# -------------------------------------------------------------------------
from celery import Celery  # noqa
mq = Celery('tasks', broker=config.BROKER_URL)

# -------------------------------------------------------------------------
# Load the app's configuration
# -------------------------------------------------------------------------
from app.helpers import LogHelper  # noqa
cache = LogHelper(app)

app.logger.info('starting application...')

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
