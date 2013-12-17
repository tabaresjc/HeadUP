from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from flask.ext.paginate import Pagination
from app import app, login_manager
from app.posts.models import Post

@app.before_request
def before_request():
    g.user = current_user

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

