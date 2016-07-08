# -*- coding: utf8 -*-

from flask import render_template, flash, redirect, session, url_for, request, g, abort, Response
from flask.ext.login import current_user, login_required
from flask.ext.paginate import Pagination
from flask.ext.babel import gettext
from app import app, babel
from app.users.models import User
from app.posts.models import Post
from app.categories.models import Category
from app.main.stamp import mod


@mod.route('/<int:id>')
def show(id):
    post = Post.get_by_id(id)
    if post is None:
        abort(404)
    return render_template("main/stamp/show.html",
                           title=gettext('Stamp | %(title)s',
                                         title=post.title),
                           post=post)


@app.route('/stamp/create', defaults={'post_id': None}, methods=['GET', 'POST'])
@app.route('/stamp/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def create_stamp(post_id):
    from app.posts.forms import PostForm, NewPostForm, EditPostForm

    if post_id:
        post = Post.get_by_id(post_id)
        if post is None:
            abort(404)
    else:
        post = None

    if request.method == 'POST':
        form = EditPostForm(id=post_id)
        if form.validate_on_submit():
            try:
                if post_id:
                    form.populate_obj(post)
                else:
                    post = Post.create()
                    form.populate_obj(post)
                    post.user = current_user
                post.save()
                flash(gettext('Stamp succesfully saved'))
                return redirect(url_for('show_stamp', post_id=post.id))
            except:
                flash(gettext('Error while posting, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
        return redirect(url_for('create_stamp', post_id=post.id))
    else:
        form = NewPostForm(post) if post_id else PostForm()
    return render_template("main/stamp/form.html",
                           form=form,
                           post=post,
                           post_id=post_id)


@app.route('/post/<int:id>', methods=['GET'])
def show_post(id):
    try:
        post = Post.get_by_id(id)
    except:
        post = None

    if post is None:
        abort(404)

    return render_template("main/post-detail.html",
                           title=gettext('Post | %(title)s', title=post.title),
                           post=post,
                           form=None)


@app.route('/category/<string:cat>', defaults={'page': 1})
@app.route('/category/<string:cat>/<int:page>')
def show_category(cat, page=1):
    limit = 5

    posts, category = Category.get_posts_by_cat(cat, limit=limit, page=page)
    total = category.posts.count()

    return render_template("main/index.html",
                           title=category.name,
                           posts=posts,
                           page=page,
                           limit=limit,
                           total=total,
                           category=category)


@app.route('/search', methods=['GET', 'POST'])
def search_post():
    form = SearchForm()
    posts = None
    count = 0
    limit = 5
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                posts, count = Search.search_post(
                    form.searchtext.data, limit=limit, page=page)
                session['search_query'] = form.searchtext.data
            except:
                flash(gettext('Error while searching, please retry later'), 'error')
        else:
            flash(gettext('Invalid submission, please check the message below'), 'error')
    else:
        if 'search_query' in session:
            form.searchtext.data = session['search_query']
            try:
                posts, count = Search.search_post(
                    form.searchtext.data, limit=limit, page=page)
            except:
                flash(gettext('Error while searching, please retry later'), 'error')

    pagination = Pagination(page=page,
                            per_page=limit,
                            total=count,
                            record_name=gettext('posts'),
                            alignment='right',
                            bs_version=3)

    return render_template("main/post-search.html",
                           title=gettext('Search'),
                           form=form,
                           posts=posts,
                           pagination=pagination)
