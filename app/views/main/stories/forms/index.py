# -*- coding: utf8 -*-

from flask import render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required
from flask_babel import gettext as _
from app.views.main.stamp import mod
from app.models import Post, Comment
from app.helpers import send_email, render_view
from .forms import CommentForm


@mod.route('/<int:id>/comment/new', methods=['GET', 'POST'])
@login_required
def comment_new(id):
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

    return render_template('main/stamp/show.html',
                           post=post,
                           form=form)


@mod.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
def comment_delete(id):
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
