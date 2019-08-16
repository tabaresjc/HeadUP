# -*- coding: utf-8 -*-

from flask_login import AnonymousUserMixin


class GuestUser(AnonymousUserMixin):

    __json_meta__ = [
        'anonymous'
    ]

    @property
    def anonymous(self):
        return True

    @property
    def timezone(self):
        return None

    @property
    def lang(self):
        return None

    def get_id(self):
        return None
