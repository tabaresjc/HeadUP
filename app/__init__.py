from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import LoginManager
from flask.ext.classy import FlaskView
from flask_wtf.csrf import CsrfProtect
from storm.locals import create_database, Store
from config import STORM_DATABASE_URI
from ago import human
import os

app = Flask(__name__)

# Load the app's configuration
app.config.from_object('config')

# Load the CSRF Protection
CsrfProtect(app)

# Database Configuration
database = create_database(STORM_DATABASE_URI)
store = Store(database)

# Load the session controller
login_manager = LoginManager()
login_manager.init_app(app)
# add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "users.login"

#----------------------------------------
# controllers
#----------------------------------------
import blog.views
import admin.views

# register the user module blueprint
from app.users.views import mod as usersModule
app.register_blueprint(usersModule, url_prefix='/users')

# check databases
if not users.models.User.exist_table():
	users.models.User.create_table()

# register the post module blueprint
from app.posts.views import PostsView
PostsView.register(app)

# check databases
if not posts.models.Post.exist_table():
	posts.models.Post.create_table()

#----------------------------------------
# filters
#----------------------------------------
def datetimeformat(value, format='%a, %d %b %Y %H:%M:%S'):
    return value.strftime(format)

def humanformat(value):
    return human(value, precision=1)

app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['humanformat'] = humanformat

