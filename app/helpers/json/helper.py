# -*- coding: utf8 -*-

from flask import request, jsonify, render_template, make_response
from flask_wtf import Form
from werkzeug.exceptions import HTTPException, NotFound
import datetime


_sucess_status_codes = [200, 204]


def render_json(message=None, status=None, error=None, **kwargs):
    """Renders the incoming data in json format."""
    status_code = 200

    if error and isinstance(error, HTTPException):
        status_code = error.code
        message = error.description
    elif error and isinstance(error, NotFound):
        status_code = 404
        message = str(error)
    elif error and isinstance(error, Exception):
        status_code = 500
        message = str(error)
    elif isinstance(status, int):
        status_code = status
    elif isinstance(status, bool):
        status_code = 200 if status else 500

    data = {
        'status': True if status_code in _sucess_status_codes else False,
        'datetime': datetime.datetime.utcnow(),
    }

    if message:
        data['message'] = message

    if kwargs:
        data['data'] = {}
        for key, obj in kwargs.iteritems():
            if isinstance(obj, Form):
                continue
            data['data'][key] = obj

    response = jsonify(**data)
    response.status_code = status_code
    return response


def render_json_template(template):
    r = make_response(render_template(template))
    r.headers.set('Content-Type', 'application/json')
    return r


def is_json_request():
    # json is the only valid format for ajax requests used in this application
    if request.is_xhr:
        return True

    is_content_json = (request.headers.get('Accept') == 'application/json' or
                       request.headers.get('Content-Type') == 'application/json')

    return is_content_json
