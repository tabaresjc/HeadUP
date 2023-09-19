# -*- coding: utf8 -*-

from flask_mail import Message
from app.helpers.tasks import task_handler
import app


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

        app.app.logger.info('Sending email to [%]' % (','.join(recipients)))
        app.mail.send(msg)
        app.app.logger.info('Sent email to [%]' % (','.join(recipients)))
    except Exception as e:
        app.app.logger.exception('Failed to send')
        app.app.logger.error(e.message)
