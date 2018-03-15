# -*- coding: utf8 -*-

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required
from flask_classy import FlaskView, route
from flask_babel import gettext
from flask_paginate import Pagination
from app.helpers import render_view
from forms import CategoryForm, TranferCatForm
from app.models import Category


class CategoriesView(FlaskView):
    route_base = '/mypage/categories'
    decorators = [login_required]

    def index(self):
        page = request.args.get('page', 1, int)

        limit = 5
        categories, total = Category.pagination(
            page=page, limit=limit, desc=False)

        categoryForm = CategoryForm()
        transferForm = TranferCatForm()

        return render_view('admin/categories/index.html',
                           page=page,
                           limit=limit,
                           total=total,
                           categories=categories,
                           categoryForm=categoryForm,
                           transferForm=transferForm)

    @route('/new', methods=['GET', 'POST'])
    def post(self):
        form = CategoryForm()
        try:
            if request.method == 'POST':
                if not form.validate():
                    raise Exception(
                        gettext('Invalid submission, please check the message below'))
                category = Category.create()
                form.populate_obj(category)

                category.slug = Category.urlify(category.slug)

                category.save()
                message = gettext('Category succesfully created')
                return render_view(url_for('CategoriesView:put', id=category.id),
                                   message=message,
                                   redirect=True)

            return render_view('admin/categories/add.html', form=form)
        except Exception as e:
            return render_view('admin/categories/add.html',
                               form=form,
                               message=str(e),
                               status=False)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        category = Category.get_by_id(id)

        if category is None:
            message = gettext('The category was not found')
            return render_view(url_for('CategoriesView:index'),
                               message=message,
                               status=False)

        if not category.can_edit():
            abort(401)

        form = CategoryForm()

        try:
            if request.method == 'POST':
                if not form.validate():
                    raise Exception(
                        gettext('Invalid submission, please check the message below'))

                form.populate_obj(category)
                category.slug = Category.urlify(category.slug)
                category.save()
                message = gettext('Category was succesfully saved')

                return render_view(url_for('CategoriesView:put', id=category.id),
                                   message=message,
                                   redirect=True)
            else:
                form.set_values(category=category)

            return render_view('admin/categories/edit.html',
                               form=form,
                               category=category)
        except Exception as e:
            return render_view('admin/categories/edit.html',
                               form=form,
                               message=str(e),
                               category=category,
                               status=False)

    @route('/remove/<int:id>', methods=['POST'])
    def delete(self, id):
        category = Category.get_by_id(id)

        try:
            if category is None:
                raise Exception(gettext('The category was not found'))

            if not category.can_edit():
                abort(401)

            if not Category.transfer_posts(category):
                raise Exception(gettext('Sorry, the last category can not be removed'))

            name = category.name
            Category.delete(category.id)
            message = gettext('The category "%(name)s" was removed', name=name)

            return render_view(url_for('CategoriesView:index'),
                               message=message,
                               redirect=True)
        except Exception as e:
            return render_view(url_for('CategoriesView:index'),
                               message=str(e),
                               redirect=True,
                               status=False)

    @route('/transfer', methods=['POST'])
    def transfer_post(self):
        try:
            trans = TranferCatForm()

            if not trans.validate_on_submit():
                raise Exception(trans.get_errors())

            cat_from = Category.get_by_id(trans.from_id.data)
            cat_to = Category.get_by_id(trans.to_id.data)

            if not cat_from or not cat_to:
                raise Exception(gettext('Either category was not found'))

            Category.transfer_posts(cat_from, cat_to)

            message = gettext('The posts were transfered from %(from_name)s to %(to_name)s',
                              from_name=cat_from.name,
                              to_name=cat_to.name)

            return render_view(url_for('CategoriesView:index'),
                               message=message, redirect=True)
        except Exception as e:
            return render_view(url_for('CategoriesView:index'),
                               message=str(e), redirect=True, status=False)
