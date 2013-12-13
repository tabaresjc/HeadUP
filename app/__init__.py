import os
from flask import Flask
from flask.ext.login import LoginManager
from storm.locals import *

from config import STORM_DATABASE_URI

from storm.locals import *

app = Flask(__name__)

# Load the app's configuration
app.config.from_object('config')

# Database Configuration
database = create_database(STORM_DATABASE_URI)
store = Store(database)

# Load the session manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Import the views
from app import views

# Import the models
from app import models