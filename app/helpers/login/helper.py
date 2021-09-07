# -*- coding: utf8 -*-

from flask import current_app, abort, request
from flask_login import LoginManager, user_unauthorized, user_needs_refresh
from app.helpers.json import is_json_request
import config


class LoginManagerHelper(LoginManager):

    def __init__(self, app, **kwargs):

        if app is None:
            raise ValueError("`app` must be an instance Flask")

        super(LoginManagerHelper, self).__init__(app=app,
                                                 **kwargs)

    def unauthorized(self, *args, **kwargs):
        if is_json_request():
            user_unauthorized.send(current_app._get_current_object())
            if self.is_api_request:
                abort(403, 'API_ERROR_INVALID_USER')
            else:
                abort(401, 'Unathorized access')

        return super(LoginManagerHelper, self).unauthorized(*args, **kwargs)

    def needs_refresh(self, *args, **kwargs):
        if is_json_request():
            user_needs_refresh.send(current_app._get_current_object())
            if self.is_api_request:
                abort(403, 'API_ERROR_INVALID_USER')
            else:
                abort(401, 'Unathorized access')

        return super(LoginManagerHelper, self).needs_refresh(*args, **kwargs)

    @property
    def auth_token(self):
        return request.headers.get(config.SESSION_AUTH_TOKEN_NAME)

    @property
    def jwt_token(self):
        token = request.headers.get(config.AUTH_HEADER_NAME) or ''

        if not token.startswith('Bearer'):
            return None

        jwt_token = token.split(' ').pop()

        return jwt_token

    @property
    def is_api_request(self):
        if self.auth_token is None:
            return request.path.startswith('/api')
        return True


