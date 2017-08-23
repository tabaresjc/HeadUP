# -*- coding: utf8 -*-

from flask import request, flash, redirect, render_template as rt, jsonify
from flask_wtf import Form

_json_header = 'application/json'


def render_template(template, status=True, message=None, **context):
    """Renders a template from the template folder with the given arguments."""

    is_content_json = (request.headers.get('Accept') == _json_header or
                       request.headers.get('Content-Type') == _json_header)

    if request.is_xhr or is_content_json:
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

    if message:
        flash(message, 'error' if not status else 'message')

    if context.get("redirect"):
        return redirect(template)

    return rt(template, **context)
