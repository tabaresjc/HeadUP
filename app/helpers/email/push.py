# -*- coding: utf8 -*-

import logging
from flask_mail import Message
from app.helpers.tasks import task_handler
import app


@task_handler
def push_email(subject, recipients, body, is_html=True):
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)
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
        logger.info('Sending email')
        app.mail.send(msg)
        logger.info('Email sent')
    except Exception:
        logger.exception('Failed to push_email')
