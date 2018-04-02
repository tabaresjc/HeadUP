# -*- coding: utf8 -*-

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required
from flask_classy import FlaskView, route
from flask_babel import gettext as _
from flask_paginate import Pagination
from app.helpers import render_view
from forms import CategoryForm, TranferForm
from app.models import Category


class CategoriesView(FlaskView):
    route_base = '/mypage/categories'
    decorators = [login_required]

    def index(self):
        page = request.args.get('page', 1, int)

        limit = 5
        categories, total = Category.pagination(page=page, limit=limit, desc=False)

        categoryForm = CategoryForm()

        return render_view('admin/categories/index.html',
                           page=page,
                           limit=limit,
                           total=total,
                           categories=categories,
                           categoryForm=categoryForm)

    @route('/new', methods=['GET', 'POST'])
    def post(self):
        form = CategoryForm()

        if form.is_submitted():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                category = Category.create()

                if not form.slug.data:
                    form.slug.data = form.name.data

                form.slug.data = Category.urlify(form.slug.data)

                form.populate_obj(category)
                category.save()

                return render_view(url_for('CategoriesView:put', id=category.id),
                                   message=_('CATEGORY_CREATE_SUCESS'),
                                   redirect=True)
            except Exception as e:
                flash(e.message, 'error')

        return render_view('admin/categories/add.html', form=form)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        category = Category.get_by_id(id)

        if category is None:
            return render_view(url_for('CategoriesView:index'),
                               status=False,
                               redirect=True,
                               message=_('CATEGORY_NOT_FOUND'))

        if not category.can_edit():
            abort(401)

        form = CategoryForm(category=category)

        if form.is_submitted():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                if not form.slug.data:
                    form.slug.data = form.name.data

                if category.slug != form.slug.data:
                    form.slug.data = Category.urlify(form.slug.data)

                form.populate_obj(category)
                category.save()

                return render_view(url_for('CategoriesView:put', id=category.id),
                                   message=_('CATEGORY_SAVE_SUCCESS'),
                                   redirect=True)
            except Exception as e:
                flash(e.message, 'error')

        return render_view('admin/categories/edit.html',
                           form=form,
                           category=category)

    @route('/remove/<int:id>', methods=['POST'])
    def delete(self, id):
        category = Category.get_by_id(id)

        try:
            if category is None:
                raise Exception(_('CATEGORY_NOT_FOUND'))

            if not category.can_edit():
                abort(401)

            if not Category.transfer_posts(category):
                raise Exception(_('CATEGORY_TRANSFER_POSTS_FAILED'))

            name = category.name
            Category.delete(category.id)

            flash(_('CATEGORY_REMOVE_SUCCESS', name=name))
        except Exception as e:
            flash(e.message, 'error')

        return render_view(url_for('CategoriesView:index'),
                           redirect=True)

    @route('/transfer', methods=['GET', 'POST'])
    def transfer_post(self):

        form = TranferForm()

        if form.is_submitted():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                cat_from = Category.get_by_id(form.from_id.data)
                cat_to = Category.get_by_id(form.to_id.data)

                if not cat_from or not cat_to:
                    raise Exception(_('CATEGORY_TRANSFER_POSTS_CHECK_FAILED'))

                Category.transfer_posts(cat_from, cat_to)

                message = _('CATEGORY_TRANSFER_POSTS_SUCCESS',
                            from_name=cat_from.name,
                            to_name=cat_to.name)

                return render_view(url_for('CategoriesView:index'),
                                   message=message,
                                   redirect=True)
            except Exception as e:
                flash(e.message, 'error')

        return render_view('admin/categories/transfer.html',
                           form=form)
