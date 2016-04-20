# -*- coding: utf8 -*-

import sys
from flask import request, json, Response, flash, redirect
from flask.ext.babel import gettext, format_datetime, format_timedelta
import truncate


def init_jinja_filters(app):
    app.jinja_env.filters['datetimeformat'] = Utilities.datetimeformat
    app.jinja_env.filters['humanformat'] = Utilities.humanformat
    app.jinja_env.filters['htmltruncate'] = truncate.html_truncate
    app.jinja_env.filters['sidebar'] = Utilities.get_navigation_bar


class Utilities(object):
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
