# -*- coding: utf8 -*-

from jinja2 import evalcontextfilter, Markup, escape
import app
import re

_paragraph_re = re.compile(r'(\r\n|\r|\n)')


@app.app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = re.sub(_paragraph_re, u'<br/>', value)

    if eval_ctx.autoescape:
        result = Markup(result)

    return result
