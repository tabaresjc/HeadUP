# -*- coding: utf8 -*-

from app import app
from flask import request
from jinja2 import evalcontextfilter


@app.template_filter()
@evalcontextfilter
def ga_autolinks(eval_ctx, items):
    domain_name = request.headers.get('HOST', '')
    if not items:
        return None

    result = []

    for item in items:
        if item != domain_name:
            result.append(u'"%s"' % item)

    return u','.join(result)
