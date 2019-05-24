# -*- coding: utf8 -*-

from app.helpers import HtmlHelper
from flask import request
from flask_babel import gettext as _, format_datetime, format_timedelta
from flask_babel import get_locale
from jinja2 import evalcontextfilter
import app
import config
import bleach


@app.app.template_filter()
@evalcontextfilter
def datetimeformat(eval_ctx, value, kind='LONG_DATETIME'):
    language_formats = config.LANGUAGES_FORMATS or {}
    language = str(get_locale())
    format = 'dd/MM/yyyy HH:mm'

    if language in language_formats:
        format = language_formats[language][kind] if kind in language_formats[language] else format

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


@app.app.template_filter()
@evalcontextfilter
def linkify(eval_ctx, value):
    if not value:
        return value

    return bleach.linkify(value)


@app.app.template_filter()
@evalcontextfilter
def urlthis(eval_ctx, value, language, scheme='http://'):
    sep = '.'

    if config.MAIN_DOMAIN.startswith('stg.'):
        sep = '-'

    if language == 'en':
        return '%s%s%s' % (scheme, config.MAIN_DOMAIN, value or '')
    else:
        return '%s%s%s%s%s' % (scheme, language, sep, config.MAIN_DOMAIN, value or '')
