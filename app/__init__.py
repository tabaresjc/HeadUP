from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import LoginManager
from flask.ext.classy import FlaskView
from flask.ext.principal import Principal
from flask_wtf.csrf import CsrfProtect
from flask.ext.babel import Babel, lazy_gettext, gettext, format_datetime, format_timedelta
from storm.locals import create_database, Store, ReferenceSet, Reference, Desc
from config import STORM_DATABASE_URI
from utilities import truncate, get_navigation_bar
import os
import datetime

app = Flask(__name__)

# Load the app's configuration
app.config.from_object('config')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# Load the CSRF Protection
CsrfProtect(app)

# Load the Babel extension for Internationalization
babel = Babel(app)

# Database Configuration
database = create_database(STORM_DATABASE_URI)
store = Store(database)

# Load the session controller
login_manager = LoginManager()
login_manager.init_app(app)
# add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "sessions.login"
login_manager.login_message = lazy_gettext('Please log in to access this page.')
#----------------------------------------
# controllers
#----------------------------------------
import blog.views
import admin.views

# register the sessions module blueprint
from app.sessions.views import mod as sessionsModule
app.register_blueprint(sessionsModule, url_prefix='/members')

# register the User module 
from app.users.views import UsersView
UsersView.register(app)

# register the Post module
from app.posts.views import PostsView
PostsView.register(app)

# register the Comment module
from app.comments.views import CommentsView
CommentsView.register(app)
#----------------------------------------
# Check Databases
#----------------------------------------
from app.users.models import User
from app.posts.models import Post
from app.comments.models import Comment


# User.posts = ReferenceSet(User.id, UserPosts.user_id, UserPosts.post_id, Post.id)
User.posts = ReferenceSet(User.id, Post.user_id, order_by = Desc(Post.id))	
Post.comments = ReferenceSet(Post.id, Comment.post_id, order_by = Comment.id)
User.comments = ReferenceSet(User.id, Comment.user_id, order_by = Desc(Comment.id))
Comment.replies = ReferenceSet(Comment.id, Comment.comment_id, order_by = Comment.id)

#----------------------------------------
# filters
#----------------------------------------
def datetimeformat(value, format='EEE, d MMM yyyy H:mm:ss'):
    return format_datetime(value,format)

def humanformat(value):
    #return human(value, precision=1)
    return gettext('Posted %(ago)s ago', ago=format_timedelta(value, granularity='second'))

def user_role(value):
    if value is users.models.ROLE_ADMIN:
    	return 'Admin'
    else:
    	return 'Writer'

def is_administrator(value):
    if value is users.models.ROLE_ADMIN:
    	return True
    else:
    	return False

def htmltruncate(value,target_len = 200, ellipsis='...'):
    return truncate(value,target_len,ellipsis)

# Get stats and values for the widgets of the blog
def get_stat(value):
    if value == 4:
        last_post, count = Post.pagination()
        return last_post
    elif value == 5:
        last_comments, count = Comment.pagination()
        return last_comments        
    else:
        return 0

app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['humanformat'] = humanformat
app.jinja_env.filters['user_role'] = user_role
app.jinja_env.filters['htmltruncate'] = htmltruncate
app.jinja_env.filters['get_stat'] = get_stat
app.jinja_env.filters['sidebar'] = get_navigation_bar
app.jinja_env.tests['administrator'] = is_administrator
