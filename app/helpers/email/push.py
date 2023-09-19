# -*- coding: utf8 -*-

from flask_mail import Message
from app.helpers.tasks import task_handler
import app


@task_handler
def push_email(subject, recipients, body, is_html=True):
    try:
        if not body or not subject or not recipients:
            return

        print(recipients)
        print(body)

        if isinstance(recipients, basestring):
            recipients = [recipients]

        msg = Message(subject, recipients=recipients)

        if is_html:
            msg.html = body
        else:
            msg.body = body
        app.app.logger.info('Sending email')
        app.mail.send(msg)
        app.app.logger.info('Email sent')
    except Exception:
        app.app.logger.exception('Failed to push_email')
