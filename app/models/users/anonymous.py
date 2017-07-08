# -*- coding: utf-8 -*-

from flask_login import AnonymousUserMixin


class GuestUser(AnonymousUserMixin):

    @property
    def timezone(self):
        return None

    @property
    def lang(self):
        return None
