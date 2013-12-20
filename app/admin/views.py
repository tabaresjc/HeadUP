from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from flask.ext.paginate import Pagination
from app import app, login_manager
from app.posts.models import Post

@app.route('/dashboard/', defaults={'page': 1})
@app.route('/dashboard/page/<int:page>')
@login_required
def dashboard(page=1):
    limit = 5
    posts = current_user.get_user_posts(page=page, limit=limit)
    pagination = Pagination(page=page, 
        per_page= limit, 
        total= current_user.posts.count(), 
        record_name= 'posts', 
        alignment = 'right', 
        bs_version= 3)

    return render_template("admin/dashboard.html",
        title = 'Blog Administration',
        posts = posts,
        pagination = pagination)
