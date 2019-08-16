# -*- coding: utf8 -*-

from flask import request
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Category


class CategoriesApiView(FlaskView):
    route_base = '/api/categories'
    decorators = []

    def index(self):
        data = request.values

        orderby = data.get('orderby', 'id', unicode)
        desc = data.get('desc', '0', unicode) == '1'

        items, count = Category.items(orderby=orderby,
                                      desc=desc)

        return render_json(items=items,
                           count=count)
