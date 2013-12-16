from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import current_user, login_required
from flask.ext.wtf import Form
from flask.ext.paginate import Pagination
from app import app, login_manager
from models import Post

from forms import PostForm
import datetime

mod = Blueprint('posts', __name__)

@mod.route('/', defaults={'page': 1})
@mod.route('/page/<int:page>')
@login_required
def index(page=1):
    form = PostForm()

    limit = 5
    pagination = Pagination(page=page, 
        per_page=limit, 
        total=current_user.posts.count(), 
        record_name='posts', 
        alignment = 'right', 
        bs_version=3)

    posts = Post.get_user_posts(user_id=current_user.id, 
        limit=limit, 
        page=page)
    
    return render_template('admin/posts/index.html', 
        title = 'Posts: Page %s' % page,
        form = form,
        posts = posts,
        pagination = pagination)  

@mod.route('/add', methods = ['GET', 'POST'])
@login_required
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

@mod.route('/view/<int:id>')
@login_required
def show(id=1):
    post = Post.get_by_id(id)

    if post is None:
        flash('The post was not found', 'error')
        return redirect(url_for('posts.index'))

    return render_template('admin/posts/show.html', 
        title = post.title,
        post = post)

@mod.route('/remove/<int:id>', methods = ['POST'])
@login_required
def destroy(id=1):
    post = Post.get_by_id(id)
    if post is None:
        flash('The post was not found', 'error')
        return redirect(url_for('posts.index'))
    title  = post.title
    Post.delete(post.id)
    flash('The post "%s" was removed' % title)
    return redirect(url_for('posts.index'))

