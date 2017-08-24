# -*- coding: utf8 -*-

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required
from flask_classy import FlaskView, route
from flask_babel import gettext
from flask_paginate import Pagination
from app.helpers import redirect_or_json, render_view
from forms import CategoryForm, NewCategoryForm, TranferCatForm
from app.models import Category


class CategoriesView(FlaskView):
    route_base = '/mypage/categories'
    decorators = [login_required]

    def index(self):
        page = request.args.get('page', 1, 'INT')

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

    @route('/', methods=['POST'])
    @route('/new', methods=['GET'])
    def post(self):
        form = CategoryForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    category = Category.create()
                    form.populate_obj(category)
                    category.save()

                    flash(gettext('Category succesfully created'))
                    return redirect_or_json(url_for('CategoriesView:index'), 'category')
                except:
                    flash(gettext('Error while creating the category'), 'error')
            else:
                flash(
                    gettext('Invalid submission, please check the message below'), 'error')
        return render_template('admin/categories/add.html',
                               title=gettext('Create Category'),
                               form=form)

    @route('/<int:id>', methods=['PUT'])
    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        category = Category.get_by_id(id)
        if category is None:
            flash(gettext('The category was not found'), 'error')
            return redirect(url_for('CategoriesView:index'))
        if not category.can_edit():
            abort(401)

        if request.method in ['POST', 'PUT']:
            form = CategoryForm()
            if form.validate_on_submit():
                try:
                    form.populate_obj(category)
                    category.save()
                    flash(gettext('Category was succesfully saved'))
                    return redirect_or_json(url_for('CategoriesView:index'), 'category')
                except:
                    return redirect_or_json(url_for('CategoriesView:index'), 'category', gettext('Error while updating the category'))
            else:
                if request.is_xhr:
                    return redirect_or_json(url_for('CategoriesView:index'), 'category', gettext('Invalid submission, please check the message below'))
                else:
                    flash(
                        gettext('Invalid submission, please check the message below'), 'error')
        else:
            form = NewCategoryForm(category)
        return render_template('admin/categories/edit.html',
                               title=gettext(
                                   'Edit Category: %(name)s', name=category.name),
                               form=form,
                               category=category)

    @route('/<int:id>', methods=['DELETE'])
    @route('/remove/<int:id>', methods=['POST'])
    def delete(self, id):
        category = Category.get_by_id(id)
        if category is None:
            flash(gettext('The category was not found'), 'error')
            return redirect(url_for('CategoriesView:index'))
        if not category.can_edit():
            abort(401)

        try:
            if not Category.transfer_posts(category):
                return redirect_or_json(url_for('CategoriesView:index'),
                                        'category',
                                        gettext('Sorry, the last category can not be removed'))

            name = category.name
            Category.delete(category.id)
            flash(gettext('The category "%(name)s" was removed', name=name))
        except:
            return redirect_or_json(url_for('CategoriesView:index'),
                                    'category',
                                    gettext('Error while removing the category'))

        return redirect_or_json(url_for('CategoriesView:index'), 'category')
