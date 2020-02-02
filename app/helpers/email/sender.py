# -*- coding: utf8 -*-

from . import actions
import config


email_actions = {
    'registration': actions.registration_email,
    'reset_password': actions.reset_password_email,
    'comment': actions.comment_email,
    'reply_comment': actions.reply_comment_email
}


def send_email(name=None, *args, **kwargs):
    if not name or not config.MAIL_SERVER:
        return

    f = email_actions.get(name)

    if not f:
        raise Exception('Unknown email action')

    f(*args, **kwargs)
