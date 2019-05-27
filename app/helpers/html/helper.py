# -*- coding: utf8 -*-

from flask import flash, redirect, render_template
from app.helpers.json import render_json, is_json_request


def render_view(path_url, status=True, message=None, **context):
    """Renders the incoming message with html/json format or redirect to the given url."""
    if is_json_request():
        return render_json(message=message, status=status, **context)

    if message:
        flash(message, 'error' if not status else 'message')

    if context.get('redirect'):
        return redirect(path_url)

    return render_template(path_url, **context)
