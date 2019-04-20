# -*- coding: utf8 -*-

from flask import request, flash, redirect, render_template as rt, jsonify
from flask_wtf import Form
import datetime

_json_header = 'application/json'


def render_view(path_url, status=True, message=None, **context):
    """Renders the incoming message with html/json format or redirect to the given url."""

    is_content_json = (request.headers.get('Accept') == _json_header or
                       request.headers.get('Content-Type') == _json_header)

    if request.is_xhr or is_content_json:
        return render_json(message=message, status=status, **context)

    if message:
        flash(message, 'error' if not status else 'message')

    if context.get("redirect"):
        return redirect(path_url)

    return rt(path_url, **context)


def render_json(status=True, message=None, **context):
    """Renders the incoming data in json format."""

    json_data = {
        'status': status,
        'datetime': datetime.datetime.utcnow(),
        'data': {}
    }

    if message:
        json_data['message'] = message

    for key, obj in context.iteritems():
        if not isinstance(obj, Form):
            json_data['data'][key] = obj

    return jsonify(**json_data)
