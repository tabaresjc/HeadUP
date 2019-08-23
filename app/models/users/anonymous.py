# -*- coding: utf-8 -*-

from flask_login import AnonymousUserMixin


class GuestUser(AnonymousUserMixin):

    __json_meta__ = [
        'anonymous',
        'is_authenticated'
    ]

    @property
    def anonymous(self):
        return True

    @property
    def is_authenticated(self):
        return False

    @property
    def timezone(self):
        return None

    @property
    def lang(self):
        return None

    def get_id(self):
        return None
