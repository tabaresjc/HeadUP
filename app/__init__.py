from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import LoginManager, current_user, login_required
from flask.ext.wtf import Form
from flask.ext.paginate import Pagination
from flask_wtf.csrf import CsrfProtect
from storm.locals import *
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

# register the user module blueprint
from app.users.views import mod as usersModule
app.register_blueprint(usersModule, url_prefix='/users')

# add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "users.login"

# check databases
if not users.models.User.exist_table():
	users.models.User.create_table()

# register the post module blueprint
from app.posts.views import mod as postsModule
from app.posts.models import Post
app.register_blueprint(postsModule, url_prefix='/posts')

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
#----------------------------------------
# controllers
#----------------------------------------
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.logoutForm = Form()

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page=1):
    limit = 5
    posts, count = Post.pagination(limit=limit,page=page)
    pagination = Pagination(page=page, 
        per_page= limit, 
        total= count, 
        record_name= 'posts', 
        alignment = 'right', 
        bs_version= 3)
    return render_template("blog/index.html",
        title = 'Home',
        content = 'Home Page',
        posts = posts,
        pagination = pagination)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("admin/dashboard.html",
        title = 'Dashboard',
        content = 'Administration Site')