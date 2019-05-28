# -*- coding: utf8 -*-

from flask import current_app, abort
from flask_login import LoginManager, user_unauthorized, user_needs_refresh
from app.helpers.json import is_json_request


class LoginManagerHelper(LoginManager):

    def __init__(self, app, **kwargs):

        if app is None:
            raise ValueError("`app` must be an instance Flask")

        super(LoginManagerHelper, self).__init__(app=app,
                                                 **kwargs)

    def unauthorized(self, *args, **kwargs):
        if is_json_request():
            user_unauthorized.send(current_app._get_current_object())
            abort(401, 'Unathorized access')

        return super(LoginManagerHelper, self).unauthorized(*args, **kwargs)

    def needs_refresh(self, *args, **kwargs):
        if is_json_request():
            user_needs_refresh.send(current_app._get_current_object())
            abort(401, 'Unathorized access')

        return super(LoginManagerHelper, self).needs_refresh(*args, **kwargs)
