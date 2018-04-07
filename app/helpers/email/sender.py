# -*- coding: utf8 -*-

import actions
import config


email_actions = {
    'registration': actions.registration_email,
    'reset_password': actions.reset_password_email,
}


def send_email(name=None, *args, **kwargs):
    if not name or not config.MAIL_SERVER:
        return

    f = email_actions.get(name)

    if not f:
        raise Exception('Unknown email')

    f(*args, **kwargs)
