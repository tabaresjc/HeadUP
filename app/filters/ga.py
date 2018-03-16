# -*- coding: utf8 -*-

from app import app
from flask import request
from jinja2 import evalcontextfilter


@app.template_filter()
@evalcontextfilter
def ga_autolinks(eval_ctx, items):
    if not items:
        return None

    domain_name = request.headers.get('HOST', '')

    result = [u'"%s"' % item for item in items if item != domain_name]

    return u','.join(result)
