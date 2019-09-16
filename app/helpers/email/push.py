# -*- coding: utf8 -*-

from flask_mail import Message
from app.helpers.tasks import task_handler
import app
import config


@task_handler
def push_email(subject, recipients, body, is_html=True):
    try:
        if not body or not subject or not recipients:
            return

        if isinstance(recipients, basestring):
            recipients = [recipients]

        msg = Message(subject, recipients=recipients)

        if is_html:
            msg.html = body
        else:
            msg.body = body

        print '*' * 100
        print recipients
        print subject
        print msg.body

        app.mail.send(msg)
    except Exception as e:
        app.logger.error(e.message)
