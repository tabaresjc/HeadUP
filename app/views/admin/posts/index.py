# -*- coding: utf8 -*-

from flask import flash, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from flask_babel import gettext
from flask_paginate import Pagination
from app.models import Post, Picture, Feed
from app.helpers import render_view
from forms import PostForm


class PostsView(FlaskView):
    route_base = '/mypage/stamps'
    decorators = [login_required]

    def index(self):
        page = request.values.get('page', 1, type=int)
        limit = 10

        posts, total = Post.posts_by_user(current_user.id,
                                          page=page, limit=limit)

        return render_view('admin/posts/index.html',
                           posts=posts,
                           page=page,
                           limit=limit,
                           total=total)

    @route('/drafts', methods=['GET'])
    def draft_list(self):
        page = request.values.get('page', 1, type=int)
        limit = 10

        posts, total = Post.posts_by_user(current_user.id,
                                          page=page,
                                          limit=limit,
                                          status=Post.POST_DRAFT)

        return render_view('admin/posts/drafts.html',
                           posts=posts,
                           page=page,
                           limit=limit,
                           total=total)

    def get(self, id):
        post = Post.get_by_id(id)

        if post is None or not post.can_edit():
            message = gettext('The requested stamp was not found')
            return render_view(url_for('PostsView:index'),
                               status=False,
                               redirect=True,
                               message=message)

        return render_view('admin/posts/show.html',
                           post=post)

    @route('/new', methods=['GET', 'POST'])
    def post(self):
        form = PostForm()
        try:
            if request.method == 'POST':
                if not form.validate():
                    raise Exception(gettext('Invalid submission, please check the message below'))

                remain = request.values.get('remain', False, bool)

                post = Post.create()
                form.populate_obj(post)
                post.user = current_user

                f = request.files.get('file')

                if f:
                    picture = Picture.create()
                    picture.save_file(f, current_user)
                    post.cover_picture_id = picture.id if picture else 0

                # init the score
                post.update_score(page_view=1)

                post.editor_version = 1
                post.save()

                Feed.clear_feed_cache()

                if post.is_draft:
                    message = gettext('Draft was succesfully saved')
                else:
                    message = gettext('Stamp was succesfully saved')

                if remain:
                    url = url_for('PostsView:put', id=post.id, remain='y')
                else:
                    url = url_for('PostsView:get', id=post.id)

                return render_view(url, redirect=True, message=message)
            else:
                message = None

            return render_view('admin/posts/edit.html',
                               form=form,
                               message=message)
        except Exception as e:
            return render_view('admin/posts/edit.html',
                               form=form,
                               message=str(e),
                               status=False)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        post = Post.get_by_id(id)

        if post is None or not post.can_edit() or post.is_hidden:
            message = gettext('The requested stamp was not found')
            return render_view(url_for('PostsView:index'),
                               redirect=True,
                               message=message,
                               status=False)
        try:
            form = PostForm()
            remain = request.values.get('remain', False, bool)

            if request.method == 'POST':
                if not form.validate():
                    raise Exception(gettext('Invalid submission, please check the message below'))

                cover_picture_id = request.values.get('cover_picture_id', 0, int)
                is_draft = request.values.get('status', 0, int) == Post.POST_DRAFT

                if post.cover_picture and cover_picture_id == 0:
                    # remove the picture, when user request its deletion
                    post.cover_picture.remove()

                form.populate_obj(post)

                f = request.files.get('file')

                if f:
                    if post.cover_picture:
                        post.cover_picture.remove()
                    picture = Picture.create()
                    picture.save_file(f, current_user)
                    post.cover_picture_id = picture.id if picture else 0

                if is_draft:
                    post.status = Post.POST_DRAFT
                else:
                    if post.save_count == 1 or post.created_at is None:
                        post.created_at = Post.current_date()
                        post.save_count = 1
                    post.status = Post.POST_PUBLIC
                    post.save_count += 1

                post.editor_version = 1
                post.save()

                Feed.clear_feed_cache()

                if post.is_draft:
                    message = gettext('Draft was succesfully saved')
                else:
                    message = gettext('Stamp was succesfully saved')

                if not remain:
                    return render_view(url_for('PostsView:get', id=post.id),
                                       redirect=True,
                                       message=message)
            else:
                form.set_values(post)
                form.remain.data = remain
                message = None

            return render_view('admin/posts/edit.html',
                               form=form,
                               post=post,
                               message=message)
        except Exception as e:
            return render_view('admin/posts/edit.html',
                               form=form,
                               post=post,
                               message=str(e),
                               status=False)

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
            Feed.clear_feed_cache()
            ret = request.values.get('return')
            message = gettext('The stamp "%(title)s" was removed', title=title)
            if ret:
                return render_view(ret, redirect=True, message=message)

            return render_view(url_for('PostsView:index'),
                               redirect=True,
                               message=message)
        except Exception as e:
            message = gettext('Error while removing the stamp, %(error)s',
                              error=e)
            return render_view(url_for('PostsView:index'),
                               status=False,
                               redirect=True,
                               message=message)
