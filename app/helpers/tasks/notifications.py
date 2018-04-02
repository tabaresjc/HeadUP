# -*- coding: utf8 -*-
from handler import task_handler


@task_handler
def push_notification(subject, recipient, html_body):
    from app.helpers import send_email

    send_email(subject, [recipient], html_body=html_body)
