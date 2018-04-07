# -*- coding: utf8 -*-

from registration import send_registration_email
import config


email_senders = {
    'registration': send_registration_email,
}


def send_email(name=None, *args, **kwargs):
    if not name or not config.MAIL_SERVER:
        return

    f = email_senders.get(name)

    if not f:
        raise Exception('Unknown email')

    f(*args, **kwargs)
