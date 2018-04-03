# -*- coding: utf-8 -*-
from flask_babel import lazy_gettext


class Role(object):
    ROLE_ADMIN = 1
    ROLE_WRITER = 2

    DEFAULT_USER_ROLES = [('2', lazy_gettext('APP_WRITER')),
                          ('1', lazy_gettext('APP_ADMIN'))]

    ROLES = {
        ROLE_ADMIN: lazy_gettext('APP_ADMIN'),
        ROLE_WRITER: lazy_gettext('APP_WRITER'),
    }
