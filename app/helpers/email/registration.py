# -*- coding: utf-8 -*-

from flask import render_template
from flask_babel import gettext
from app.helpers.tasks import register_notification


def send_registration_email(user):
    import config
    if isinstance(user, (int, long)):
        from app.models import User
        user = User.get_by_id(user)
        if not user:
            return

    subject = gettext('EMAIL_REGISTRATION_TITLE', name=config.SITE_NAME)

    html_body = render_template(
        'emails/users/registration.html',
        user=user,
        title=subject)

    register_notification.delay(
        subject,
        user.email,
        html_body)
