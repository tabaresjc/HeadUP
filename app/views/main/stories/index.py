# -*- coding: utf8 -*-

from flask import render_template, url_for, abort, send_file, session, flash, redirect
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from flask_babel import gettext as _
from app.models import Post, Feed, Category, Comment
from app.helpers import send_email, render_view, nocache
from forms import CommentForm
import datetime
import config


class StoriesView(FlaskView):
    route_base = '/stories'

    @route('/<int:id>', endpoint='story.show')
    def show(self, id):
        post = Post.get_by_id(id)

        if post is None or post.is_hidden:
            abort(404)

        form = CommentForm()

        return render_template('main/stories/show.html',
                               post=post,
                               form=form)

    @route('/new', endpoint='story.new')
    @login_required
    def new(self):

        return render_template('main/stories/edit.html',
                               id=0,
                               post=None)

    @route('/edit/<int:id>', endpoint='story.edit')
    @login_required
    def edit(self, id):

        post = Post.get_by_id(id)

        if post is None or post.is_hidden:
            abort(404)

        if not post.can_edit():
            abort(403)

        return render_template('main/stories/edit.html',
                               id=id,
                               post=post)

    @route('/category/<string:slug>', endpoint='story.category')
    def category(self, slug):
        category = Category.get_by_cat(slug)
        page = 1

        if not category:
            abort(404)

        return render_template('main/stories/category.html',
                               category=category,
                               page=page)

    @route('/<int:id>/comment/new', methods=['GET', 'POST'], endpoint='story.comment_new')
    @login_required
    def comment_new(self, id):
        post = Post.get_by_id(id)

        if post is None or post.is_hidden:
            abort(404)

        form = CommentForm()

        if form.is_submitted():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                comment = Comment(user=current_user, post=post)
                form.populate_obj(comment)
                comment.save()

                flash(_('COMMENT_SAVE_SUCESS'))

                if comment.parent_comment:
                    send_email('reply_comment', comment)
                else:
                    send_email('comment', post, comment)

                return redirect(url_for('story.show',
                                        id=post.id,
                                        _anchor='comment-%s' % comment.id))

            except Exception as e:
                flash(e.message, 'error')

        return render_template('main/stories/show.html',
                               post=post,
                               form=form)

    @route('/comment/<int:id>/delete', methods=['POST'], endpoint='story.comment_delete')
    @login_required
    def comment_delete(self, id):
        comment = Comment.get_by_id(id)

        if comment is None or not comment.can_delete:
            abort(403)

        post = comment.post

        try:
            Comment.delete(id)
            message = _('COMMENT_DELETE_SUCCESS')
        except Exception as e:
            message = _('ERROR_COMMENT_DELETE_FAILED', error=e)

        return render_view(url_for('story.show', id=post.id),
                           redirect=True,
                           message=message)

    @route('/counter/<string:post_id>.gif', endpoint='story.count_page_view')
    @nocache
    def count_page_view(self, post_id):

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
                seconds = datetime.datetime.now() + datetime.timedelta(hours=8)
                session[key] = Feed.epoch_seconds(seconds)

        except Exception as e:
            Post.rollback_transaction()
            raise e

        return send_file(config.BASE_DIR + '/static/images/counter.gif', mimetype='image/gif')
