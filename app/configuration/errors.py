# -*- coding: utf8 -*-

from flask import render_template
from werkzeug.exceptions import HTTPException
from app.helpers import render_json, is_json_request
from app import app
import config


def register_error_handlers():
    app.register_error_handler(401, internal_http_error)
    app.register_error_handler(403, internal_http_error)
    app.register_error_handler(404, internal_http_error)
    app.register_error_handler(500, internal_http_error)
    app.register_error_handler(HTTPException, internal_http_error)

    if not config.DEBUG:
        app.register_error_handler(Exception, internal_server_error)


def internal_http_error(error):
    app.logger.error('Internal HTTP Exception, code[%s] => %s',
                     error.code,
                     error)

    if is_json_request():
        return render_json(error=error)

    template = 'errors/500.html'

    if error.code in [401, 403, 404]:
        template = 'errors/%s.html' % error.code

    return render_template(template, title=error), error.code


def internal_server_error(error):
    app.logger.error('Internal server error => %s',
                     error)

    if is_json_request():
        return render_json(error=error)

    return render_template('errors/500.html', title=error), 500


register_error_handlers()
