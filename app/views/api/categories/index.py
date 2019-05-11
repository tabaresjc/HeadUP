# -*- coding: utf8 -*-

from flask import request
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Category


class ApiCategoriesView(FlaskView):
    route_base = '/api/categories'
    decorators = []

    def index(self):
        try:
            data = request.values

            orderby = data.get('orderby', u'id', unicode)
            desc = data.get('desc', u'0', unicode) == '1'

            items, count = Category.items(orderby=orderby, desc=desc)

            return render_json(items=items, count=count)
        except Exception as e:
            return render_json(status=False, message=e.message)
