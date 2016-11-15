# -*- coding: utf8 -*-

from flask import render_template, redirect, url_for, abort, send_file
from app import app
from app.models import Post
from app.main.stamp import mod


@mod.route('/<int:id>')
def show(id):
    post = Post.get_by_id(id)
    if post is None:
        abort(404)
    return render_template("main/stamp/show.html",
                           post=post)


@mod.route('/edit/<int:id>')
def edit(id):
    post = Post.get_by_id(id)
    if post is None:
        abort(404)
    return redirect(url_for('PostsView:put', id=post.id))


@mod.route('/new')
def new():
    return redirect(url_for('PostsView:post'))


@mod.route('/counter/<string:post_id>.gif')
def count_page_view(post_id):
    id = Post.decode_id(post_id)

    try:
        Post.begin_transaction()
        post = Post.get_by_id(id)
        post.update_score(page_view=1)
        post.save()
        Post.commit_transaction()
    except Exception as e:
        Post.rollback_transaction()
        raise e

    return send_file('static/theme/headsup/images/counter.gif', mimetype='image/gif')
