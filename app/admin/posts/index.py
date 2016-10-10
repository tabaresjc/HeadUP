# -*- coding: utf8 -*-

from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask.ext.login import current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.babel import gettext
from flask.ext.paginate import Pagination
from app.models import Post
from forms import PostForm, EditPostForm, NewPostForm


class PostsView(FlaskView):
    route_base = '/mypage/stamps'
    decorators = [login_required]

    def index(self):
        page = request.values.get('page', 1, type=int)
        limit = 10
        posts, total = Post.posts_by_user(current_user.id, page=page, limit=limit)
        return render_template('admin/posts/index.html',
                               posts=posts,
                               page=page,
                               limit=limit,
                               total=total)

    def get(self, id):
        post = Post.get_by_id(id)

        if post is None or not post.can_edit():
            flash(gettext('The requested stamp was not found'), 'error')
            return redirect(url_for('PostsView:index'))

        return render_template('admin/posts/show.html',
                               title=post.title,
                               post=post)

    @route('/', methods=['POST'])
    @route('/new', methods=['GET'])
    def post(self):
        form = PostForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    post = Post.create()
                    form.populate_obj(post)
                    post.user = current_user
                    post.save()
                    flash(gettext('Stamp succesfully created'))
                    return redirect(url_for('PostsView:index'))
                except Exception as e:
                    flash(gettext('Error while creating the stamp, %(error)s', error=e), 'error')
            else:
                flash(
                    gettext('Invalid submission, please check the message below'), 'error')

        return render_template('admin/posts/add.html', form=form)

    @route('/<int:id>', methods=['PUT'])
    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        post = Post.get_by_id(id)

        if post is None or not post.can_edit():
            flash(gettext('The requested stamp was not found'), 'error')
            return redirect(url_for('PostsView:index'))

        if request.method in ['POST', 'PUT']:
            form = EditPostForm(id=id)
            if form.validate_on_submit():
                try:
                    form.populate_obj(post)
                    post.save()
                    flash(gettext('Stamp was succesfully saved'))
                    if request.method == 'POST':
                        if form.remain.data:
                            return redirect(url_for('PostsView:put_0', id=post.id))
                        else:
                            return redirect(url_for('PostsView:get', id=post.id))
                except Exception as e:
                    flash(gettext('Error while updating the stamp, %(error)s', error=e), 'error')
            else:
                flash(
                    gettext('Invalid submission, please check the message below'), 'error')

            if request.method == 'PUT':
                return jsonify(redirect_to=url_for('PostsView:index'))
        else:
            form = NewPostForm(post)

        return render_template('admin/posts/edit.html', form=form, post=post)

    @route('/<int:id>', methods=['DELETE'])
    @route('/remove/<int:id>', methods=['POST'])
    def delete(self, id):
        post = Post.get_by_id(id)

        if post is None:
            flash(gettext('The stamp was not found'), 'error')
            return redirect(url_for('PostsView:index'))

        if not post.can_edit():
            abort(401)

        try:
            title = post.title
            Post.delete(post.id)
            flash(gettext('The stamp "%(title)s" was removed', title=title))
        except Exception as e:
            flash(gettext('Error while removing the stamp, %(error)s', error=e), 'error')

        if request.method == 'POST':
            return redirect(url_for('PostsView:index'))
        return jsonify(redirect_to=url_for('PostsView:index'))
