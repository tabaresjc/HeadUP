# -*- coding: utf8 -*-

import sys
import datetime
from app import app
from flask import request, json, Response, flash, redirect
from flask.ext.babel import gettext, format_datetime, format_timedelta
from flask.ext.paginate import Pagination
from jinja2 import evalcontextfilter, Markup, escape
import truncate
import re

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


def init_jinja_filters(app):
    app.jinja_env.filters['datetimeformat'] = Utilities.datetimeformat
    app.jinja_env.filters['humanformat'] = Utilities.humanformat
    app.jinja_env.filters['htmltruncate'] = truncate.html_truncate
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.context_processor
def utility_processor():
    # Site name
    from config import SITE_NAME
    # Send the current date & time
    today = datetime.date.today()

    def pag(name, page, limit, total, record_name, alignment='right', bs_version=3, kind=None, **kwargs):
        name = u'%s.%s.%s.%s.%s.%s.%s' % (
            name, page, limit, total, record_name, alignment, bs_version)
        pagination = Utilities.get_pagination_by_name(name)

        if not pagination:
            pagination = Pagination(page=page, per_page=limit, total=total,
                                    record_name=record_name, alignment=alignment, bs_version=bs_version, **kwargs)
            Utilities.set_pagination_by_name(name, pagination)

        if kind == 'links':
            return pagination.links
        elif kind == 'info':
            return pagination.info
        else:
            return pagination

    return dict(pag=pag,
                today=today,
                site_name=SITE_NAME)


class Utilities(object):

    @staticmethod
    def get_pagination_by_name(name):
        if not name:
            return None
        try:
            pages_obj = Utilities.pages_obj
        except AttributeError:
            pages_obj = dict()
            Utilities.pages_obj = pages_obj
        return pages_obj.get(name, None)

    @staticmethod
    def set_pagination_by_name(name, pagination):
        if not name:
            return None
        try:
            pages_obj = Utilities.pages_obj
        except AttributeError:
            pages_obj = dict()
            Utilities.pages_obj = pages_obj
        Utilities.pages_obj[name] = pagination

    @staticmethod
    def redirect_json_or_html(url, type, message=''):
        if request.is_xhr:
            if message:
                js = [{"result": "error", "message": message,
                       "type": "category", "redirect": url}]
            else:
                js = [{"result": "ok", "type": "category", "redirect": url}]
            return Response(json.dumps(js), mimetype='application/json')
        else:
            if message:
                flash(message, 'error')
            return redirect(url)

    @staticmethod
    def datetimeformat(value, format='EEE, d MMM yyyy H:mm:ss'):
        return format_datetime(value, format)

    @staticmethod
    def humanformat(value):
        # return human(value, precision=1)
        return gettext('Posted %(ago)s ago', ago=format_timedelta(value, granularity='second'))
