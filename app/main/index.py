# -*- coding: utf8 -*-

from flask import render_template, redirect, url_for, request
from app import app
from app.posts.models import Post


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page=1):
    limit = 20
    posts, total = Post.pagination(limit=limit, page=page)
    if not posts.count() and page > 1:
        return redirect(url_for('index'))
    return render_template("main/index.html",
                           posts=posts,
                           page=page,
                           limit=limit,
                           total=total)
