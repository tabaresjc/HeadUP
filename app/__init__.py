from flask import Flask, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import LoginManager
from flask.ext.classy import FlaskView
from flask.ext.principal import Principal
from flask_wtf.csrf import CsrfProtect
from storm.locals import create_database, Store, ReferenceSet, Reference, Desc
from config import STORM_DATABASE_URI
from ago import human
import os
import datetime

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
login_manager.login_view = "sessions.login"

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

def init_db():
	user = User.create()
	user.name = u'Juan Tabares'
	user.nickname = u'jctt'
	user.set_password(u'admin123456')
	user.role = 1
	user.email = u'juan.ctt@live.com'
	user.last_seen = datetime.datetime.now()
	user.save()

	user1 = User.create()
	user1.name = u'Mrs. Arnaldo Wyman'
	user1.nickname = u'arnaldo'
	user1.set_password(u'admin123456')
	user1.email = u'example-2@railstutorial.org'
	user1.last_seen = datetime.datetime.now()
	user1.save()

def create_db():
	# Posts
	if not Post.exist_table():
		Post.create_table()

	# Comments
	if not Comment.exist_table():
		Comment.create_table()

	# Users
	if not User.exist_table():
		User.create_table()
		init_db()


def create_posts():
	user = User.get_by_id(1)
	for i in range(1, 50):
		print 'creating post # %s' %i
		post = Post.create()
		post.title = unicode('Title %s' % i)
		post.body = unicode('Body %s' % i)
		post.user = user
		post.save()

create_db()

# User.posts = ReferenceSet(User.id, UserPosts.user_id, UserPosts.post_id, Post.id)
User.posts = ReferenceSet(User.id, Post.user_id, order_by = Desc(Post.id))	
Post.comments = ReferenceSet(Post.id, Comment.post_id, order_by = Comment.id)
User.comments = ReferenceSet(User.id, Comment.user_id, order_by = Desc(Comment.id))	
#----------------------------------------
# filters
#----------------------------------------
def datetimeformat(value, format='%a, %d %b %Y %H:%M:%S'):
    return value.strftime(format)

def humanformat(value):
    return human(value, precision=1)

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

app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['humanformat'] = humanformat
app.jinja_env.filters['user_role'] = user_role
app.jinja_env.tests['administrator'] = is_administrator
