# -*- coding: utf-8 -*-
from flask.ext.babel import lazy_gettext


class Role(object):
    ROLE_ADMIN = 1
    ROLE_WRITER = 2

    ROLES = {
        ROLE_ADMIN: lazy_gettext('Admin'),
        ROLE_WRITER: lazy_gettext('Writer'),
    }
