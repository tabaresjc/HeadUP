# -*- coding: utf-8 -*-
from flask_babel import lazy_gettext as _lg


class Role(object):
    ROLE_ADMIN = 1
    ROLE_WRITER = 2

    DEFAULT_USER_ROLES = [('2', _lg('APP_WRITER')),
                          ('1', _lg('APP_ADMIN'))]

    ROLES = {
        ROLE_ADMIN: _lg('APP_ADMIN'),
        ROLE_WRITER: _lg('APP_WRITER'),
    }
