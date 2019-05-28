# -*- coding: utf8 -*-

from flask import render_template
from werkzeug.exceptions import HTTPException
from app.helpers import render_json, is_json_request


class ErrorHelper(object):

    def __init__(self, app, **kwargs):

        if app is None:
            raise ValueError("`app` must be an instance Flask")

        self.app = app
        self._set_errors()

    def _set_errors(self):
        self.app.register_error_handler(401, self._internal_http_error)
        self.app.register_error_handler(403, self._internal_http_error)
        self.app.register_error_handler(404, self._internal_http_error)
        self.app.register_error_handler(500, self._internal_http_error)
        self.app.register_error_handler(HTTPException,
                                        self._internal_http_error)

        if not self.app.config.get('DEBUG'):
            self.app.register_error_handler(Exception,
                                            self._internal_server_error)

    def _internal_http_error(self, error):
        self.app.logger.error('Internal HTTP Exception, code[%s] => %s',
                              error.code,
                              error)

        if is_json_request():
            return render_json(error=error)

        template = 'errors/500.html'

        if error.code in [401, 403, 404]:
            template = 'errors/%s.html' % error.code

        return render_template(template, title=error), error.code

    def _internal_server_error(self, error):
        self.app.logger.error('Internal server error => %s',
                              error)

        if is_json_request():
            return render_json(error=error)

        return render_template('errors/500.html', title=error), 500
