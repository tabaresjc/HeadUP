# -*- coding: utf8 -*-

from app.helpers import HtmlHelper
from flask import request
from flask_babel import gettext as _, format_datetime, format_timedelta
from jinja2 import evalcontextfilter
import app


@app.app.template_filter()
@evalcontextfilter
def datetimeformat(eval_ctx, value, format='EEE, d MMM yyyy H:mm:ss'):
    return format_datetime(value, format)


@app.app.template_filter()
@evalcontextfilter
def humanformat(eval_ctx, value):
    if not value:
        return ''

    return _('APP_PUBLISHED_AGO', ago=format_timedelta(value, granularity='second'))


@app.app.template_filter()
@evalcontextfilter
def limit(eval_ctx, inputstr, total, ellipsis='...'):
    if not inputstr:
        return inputstr

    if not isinstance(inputstr, basestring):
        inputstr = unicode(inputstr)
    elif not isinstance(inputstr, unicode):
        inputstr = unicode(inputstr, 'utf-8', 'strict')

    if total >= len(inputstr):
        return inputstr

    return u''.join([inputstr[:total], ellipsis])


@app.app.template_filter()
@evalcontextfilter
def htmltruncate(eval_ctx, value, target_len=200, ellipsis='...'):
    return HtmlHelper.truncate(value, target_len, ellipsis)
