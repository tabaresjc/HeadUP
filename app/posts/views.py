from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import current_user, login_required
from flask.ext.wtf import Form
from app import app, login_manager
from models import Post

from forms import PostForm
import datetime

mod = Blueprint('posts', __name__)

@mod.route('/')
@mod.route('/index')
@login_required
def index():
	form = PostForm()
	posts = current_user.posts
	return render_template('admin/posts/index.html', 
        title = 'Posts',
        form = form,
        posts = posts)  

@mod.route('/add', methods = ['GET', 'POST'])
def create():    
    form = PostForm()
    if form.validate_on_submit():
    	try:
    		post = Post.create()
    		form.populate_obj(post)
    		current_user.posts.add(post)
    		post.save()

    		flash('Post succesfully created')
    		return redirect(url_for('posts.index'))
    	except:
    		raise
    return render_template('admin/posts/add.html', 
        title = 'Create Post',
        form = form)   