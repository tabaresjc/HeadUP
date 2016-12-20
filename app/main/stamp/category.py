# -*- coding: utf8 -*-

from flask import render_template, abort
from app import app
from app.main.stamp import mod
from app.models import Category


@mod.route('/category/<string:slug>')
@mod.route('/category/<string:slug>/page/<int:page>')
def category(slug, page=1):
    category = Category.get_by_cat(slug)

    if not category:
        abort(404)

    return render_template('main/stamp/category.html',
                           category=category,
                           page=page)
