from flask import Flask
from flask.ext.login import LoginManager, current_user
from flask_wtf.csrf import CsrfProtect
from flask.ext.babel import Babel, lazy_gettext

from werkzeug import LocalProxy, cached_property, ImmutableDict
from werkzeug.contrib.fixers import ProxyFix

from storm.locals import create_database, Store, ReferenceSet, Desc
from config import STORM_DATABASE_URI
import flask

import os

app = Flask(__name__)
if os.environ.get('HEROKU') is None:
  app.debug = True

#--------------------------------------------------------------------------------
# Load the app's configuration
#--------------------------------------------------------------------------------
app.config.from_object('config')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

#--------------------------------------------------------------------------------
# Load the CSRF Protection
#--------------------------------------------------------------------------------
csrf = CsrfProtect()
csrf.init_app(app)

#--------------------------------------------------------------------------------
# Load the Babel extension for Internationalization
#--------------------------------------------------------------------------------
babel = Babel(app)

@babel.localeselector
def get_locale():
    if current_user and current_user.is_authenticated:
        return current_user.lang
    return request.accept_languages.best_match(LANGUAGES.keys())


@babel.timezoneselector
def get_timezone():
    if current_user and current_user.is_authenticated:
        return current_user.timezone
    return "Asia/Tokyo"

#--------------------------------------------------------------------------------
# Database Configuration
#--------------------------------------------------------------------------------
def get_db_connection():
  try:
    if not flask.g.db:
      raise AttributeError()
  except (KeyError, AttributeError):
    flask.g.db = Store(create_database(STORM_DATABASE_URI))
  return flask.g.db

def close_db_connection():
  try:
    if flask.g.db:
      flask.g.db.rollback()
      flask.g.db.close()
      flask.g.db = None
      del flask.g.db
  except (KeyError, AttributeError):
    pass

def request_finished_handler(sender, response):
  after_request_handler(response)

def got_request_exception_handler(sender, exception):
  after_request_handler()

flask.request_finished.connect(request_finished_handler, app)
flask.got_request_exception.connect(got_request_exception_handler, app)

store = LocalProxy(get_db_connection)

#--------------------------------------------------------------------------------
# Load the session controller
#--------------------------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
# add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "sessions.login"
login_manager.login_message = lazy_gettext('Please log in to access this page.')

#--------------------------------------------------------------------------------
# Register Views
#--------------------------------------------------------------------------------
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

# register the Category module
from app.categories.views import CategoriesView
CategoriesView.register(app)

#--------------------------------------------------------------------------------
# Register the models and their references
#--------------------------------------------------------------------------------
from app.users.models import User
from app.posts.models import Post
from app.comments.models import Comment
from app.categories.models import Category

# User.posts = ReferenceSet(User.id, UserPosts.user_id, UserPosts.post_id, Post.id)
User.posts = ReferenceSet(User.id, Post.user_id, order_by=Desc(Post.id))
Post.comments = ReferenceSet(Post.id, Comment.post_id, order_by=Comment.id)
User.comments = ReferenceSet(User.id, Comment.user_id, order_by=Desc(Comment.id))
Comment.replies = ReferenceSet(Comment.id, Comment.comment_id, order_by=Comment.id)
Category.posts = ReferenceSet(Category.id, Post.category_id, order_by=Post.id)

#--------------------------------------------------------------------------------
# Register the filters
#--------------------------------------------------------------------------------
from utils import init_jinja_filters
init_jinja_filters(app)

#--------------------------------------------------------------------------------
# Application's event handlers
#--------------------------------------------------------------------------------
@app.after_request
def after_request_handler(response=None):
  close_db_connection()
  return response

@app.before_request
def before_request(response=None):
    close_db_connection()
    if flask.request.endpoint:
        if 'redirect_to' in flask.session and flask.request.endpoint not in ['static', 'sessions.login', 'sessions.signup', 'sessions.login_comment']:
            flask.session.pop('redirect_to', None)
    return response


if app.debug:
    import sys
    from storm.tracer import debug
    debug(True, stream=sys.stdout)
