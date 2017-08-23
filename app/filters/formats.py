# -*- coding: utf8 -*-

from app import app
from app.helpers import HtmlHelper
from flask import request
from flask_babel import gettext, format_datetime, format_timedelta
from jinja2 import evalcontextfilter


@app.template_filter()
@evalcontextfilter
def datetimeformat(eval_ctx, value, format='EEE, d MMM yyyy H:mm:ss'):
    return format_datetime(value, format)


@app.template_filter()
@evalcontextfilter
def humanformat(eval_ctx, value):
    if not value:
        return ''

    return gettext('Posted %(ago)s ago',
                   ago=format_timedelta(value, granularity='second'))


@app.template_filter()
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


@app.template_filter()
@evalcontextfilter
def htmltruncate(eval_ctx, value, target_len=200, ellipsis='...'):
    return HtmlHelper.truncate(value, target_len, ellipsis)
