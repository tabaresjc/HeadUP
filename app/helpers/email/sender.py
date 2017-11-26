# -*- coding: utf8 -*-

from flask import render_template
from flask_mail import Message
import app


def send_email(subject, recipients, text_body=None, html_body=None):
    try:
        msg = Message(subject, recipients=recipients)

        if not text_body and not html_body:
            return

        if text_body:
            msg.body = text_body
        if html_body:
            msg.html = html_body

        app.mail.send(msg)
    except:
        pass
