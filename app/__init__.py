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
# Socket IO Configuration
# -------------------------------------------------------------------------
from flask_socketio import SocketIO  # noqa
socketio = SocketIO(app,
                    logger=config.SOCKET_IO_LOGGER_ENABLED,
                    engineio_logger=config.SOCKET_IO_ENGINEIO_LOGGER_ENABLED,
                    cors_allowed_origins=config.SOCKET_IO_CORS_ALLOWED_ORIGINS)

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
wg = Widgets(app)

# -------------------------------------------------------------------------
# Load the session controller
# -------------------------------------------------------------------------
from helpers import LoginManagerHelper  # noqa
login_manager = LoginManagerHelper(app)

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
# Load micawber for oembed
# -------------------------------------------------------------------------
from micawber.providers import bootstrap_basic  # noqa
from micawber.contrib.mcflask import add_oembed_filters  # noqa

oembed_providers = bootstrap_basic()
add_oembed_filters(app, oembed_providers)

# -------------------------------------------------------------------------
# Load the app's configuration
# -------------------------------------------------------------------------
from app.helpers import LogHelper  # noqa
logger = LogHelper(app)

# -------------------------------------------------------------------------
# Cache Configuration
# -------------------------------------------------------------------------
from app.helpers import CacheHelper  # noqa
cache = CacheHelper(app)

# -------------------------------------------------------------------------
# Campaign Configuration
# -------------------------------------------------------------------------
from app.helpers import CampaignHelper  # noqa
campaign = CampaignHelper(app)

# -------------------------------------------------------------------------
# Error Configuration
# -------------------------------------------------------------------------
from app.helpers import ErrorHelper  # noqa
ErrorHelper(app)

# -------------------------------------------------------------------------
# Register modules of the application
# -------------------------------------------------------------------------
import configuration  # noqa
import helpers  # noqa
import filters  # noqa
import models  # noqa
import views  # noqa
import widgets  # noqa
import events  # noqa
