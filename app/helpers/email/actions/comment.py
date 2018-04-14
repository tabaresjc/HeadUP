# -*- coding: utf-8 -*-

from flask import render_template
from flask_babel import gettext as _
from app.helpers.email.push import push_email
import config


def comment_email(post, comment):
    if not post or not post.user or not comment:
        return

    user = post.user
    title = post.title[:75] + (post.title[75:] and '...')

    subject = _('EMAIL_COMMENT_TITLE',
                name=comment.user.name,
                title=title)

    body = render_template('emails/users/comment.html',
                           post=post,
                           user=user,
                           comment=comment,
                           title=subject)

    push_email.delay(subject, user.email, body)


def reply_comment_email(comment):
    if (not comment or
            not comment.parent_comment or
            not comment.parent_comment.user):
        return

    user = comment.parent_comment.user
    post = comment.post
    title = post.title[:75] + (post.title[75:] and '...')

    subject = _('EMAIL_REPLY_COMMENT_TITLE',
                name=comment.user.name,
                title=title)

    body = render_template('emails/users/reply_comment.html',
                           post=post,
                           user=user,
                           comment=comment,
                           title=subject)

    push_email.delay(subject, user.email, body)
