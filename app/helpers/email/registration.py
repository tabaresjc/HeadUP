# -*- coding: utf-8 -*-

from flask import render_template
from flask_babel import gettext as _
from app.helpers import push_notification
import config


def send_registration_email(user):
    cfg = config.__dict__

    if not cfg.get('MAIL_SERVER'):
        return

    if isinstance(user, (int, long)):
        from app.models import User
        user = User.get_by_id(user)
        if not user:
            return

    subject = _('EMAIL_REGISTRATION_TITLE', name=config.SITE_NAME)

    html_body = render_template(
        'emails/users/registration.html',
        user=user,
        title=subject)

    push_notification.delay(
        subject,
        user.email,
        html_body)
