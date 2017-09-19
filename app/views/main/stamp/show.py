# -*- coding: utf8 -*-

from flask import render_template, redirect, url_for, abort, send_file, session
from app import app
from app.models import Post
from . import mod
from app.helpers import nocache
from config import BASE_DIR


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
@nocache
def count_page_view(post_id):
    from app.models import Feed
    import datetime
    id = Post.decode_id(post_id)
    post = Post.get_by_id(id)
    try:
        key = u'counter_post_%s' % id
        count_time = float(session[key]) if key in session else 0

        # Increase pageviews in 1 hour
        if Feed.epoch_seconds(datetime.datetime.now()) > count_time:
            Post.begin_transaction()
            post.update_score(page_view=1)
            post.save()
            Post.commit_transaction()
            session[key] = Feed.epoch_seconds(
                datetime.datetime.now() + datetime.timedelta(hours=8))

    except Exception as e:
        Post.rollback_transaction()
        raise e
    return send_file(BASE_DIR + '/static/images/counter.gif', mimetype='image/gif')
