# -*- coding: utf-8 -*-

from flask import render_template
from flask_babel import gettext as _
from app.helpers.email.push import push_email
import config


def registration_email(user):
    if not user:
        return

    subject = _('EMAIL_REGISTRATION_TITLE', name=config.SITE_NAME)

    body = render_template('emails/users/registration.html',
                           user=user,
                           title=subject)

    push_email.delay(subject, user.email, body)
