# -*- coding: utf8 -*-

import sys
from app import app
from flask import request, json, Response, flash, redirect
from flask.ext.babel import gettext, format_datetime, format_timedelta
from flask.ext.paginate import Pagination
import truncate


def init_jinja_filters(app):
    app.jinja_env.filters['datetimeformat'] = Utilities.datetimeformat
    app.jinja_env.filters['humanformat'] = Utilities.humanformat
    app.jinja_env.filters['htmltruncate'] = truncate.html_truncate
    app.jinja_env.filters['sidebar'] = Utilities.get_navigation_bar
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

@app.context_processor
def utility_processor():
    def pag(name, page, per_page, total, record_name, alignment = 'right', bs_version = 3, kind = None, **kwargs):
        name = u'%s.%s.%s.%s.%s.%s.%s' % (name, page, per_page, total, record_name, alignment, bs_version)
        pagination = Utilities.get_pagination_by_name(name)

        if not pagination:
            pagination = Pagination(page=page, per_page=per_page, total=total, record_name=record_name, alignment=alignment, bs_version=bs_version, **kwargs)
            Utilities.set_pagination_by_name(name, pagination)

        if kind == 'links':
            return pagination.links
        elif kind == 'info':
            return pagination.info
        else:
            return pagination
    return dict(pag=pag)


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
                js = [{"result": "error", "message": message, "type": "category", "redirect": url}]
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
        #return human(value, precision=1)
        return gettext('Posted %(ago)s ago', ago=format_timedelta(value, granularity='second'))

    @staticmethod
    def get_navigation_bar(value, sorted=True):
        d = dict([
            (0, {
                'name': 'Dashboard',
                'url': 'dashboard',
                'icon': 'icon-home',
                'pattern': 'dashboard'
            }),
            (1, {
                'name': 'Posts',
                'url': '',
                'icon': 'icon-edit',
                'pattern': 'PostsView',
                'sub-menu': {
                    'index': {
                        'name': 'Post List',
                        'url': 'PostsView:index'
                    },
                    'new': {
                        'name': 'New Post',
                        'url': 'PostsView:post_0'
                    }
                }
            }),
            (3, {
                'name': 'Categories',
                'require_admin': True,
                'url': 'CategoriesView:index',
                'icon': 'icon-bookmark',
                'pattern': 'CategoriesView'
            }),
            (4, {
                'name': 'Users',
                'require_admin': True,
                'url': '',
                'icon': 'icon-user',
                'pattern': 'UsersView',
                'sub-menu': {
                    'index': {
                        'name': 'User List',
                        'url': 'UsersView:index'
                    },
                    'new': {
                        'name': 'New User',
                        'url': 'UsersView:post_0'
                    }
                }
            })
        ])
        return d
