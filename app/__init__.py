from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import LoginManager
from flask.ext.classy import FlaskView
from flask.ext.principal import Principal
from flask_wtf.csrf import CsrfProtect
from flask.ext.babel import Babel, lazy_gettext
from storm.locals import create_database, Store, ReferenceSet, Reference, Desc
from config import STORM_DATABASE_URI
from utilities import Utilities

import os


app = Flask(__name__)

# Load the app's configuration
app.config.from_object('config')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# Load the CSRF Protection
csrf = CsrfProtect()
csrf.init_app(app)

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

app.jinja_env.filters['datetimeformat'] = Utilities.datetimeformat
app.jinja_env.filters['humanformat'] = Utilities.humanformat
app.jinja_env.filters['htmltruncate'] = Utilities.htmltruncate
app.jinja_env.filters['get_stat'] = blog.models.get_stat
app.jinja_env.filters['sidebar'] = Utilities.get_navigation_bar
