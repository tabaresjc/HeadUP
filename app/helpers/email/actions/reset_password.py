# -*- coding: utf-8 -*-

from flask import render_template
from flask_babel import gettext as _
from app.helpers.email.push import push_email
import config


def reset_password_email(user):
    if not user:
        return

    subject = _('EMAIL_RESET_PASSWORD_TITLE', email=user.email)

    body = render_template('emails/users/reset_password.html',
                           user=user,
                           title=subject)

    push_email.delay(subject, user.email, body)
