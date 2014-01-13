from flask import render_template, flash, redirect, url_for, request, abort
from flask.ext.login import login_required
from flask.ext.classy import FlaskView, route
from flask.ext.babel import gettext
from flask.ext.paginate import Pagination
from app import Utilities as util
from forms import CategoryForm, NewCategoryForm, TranferCatForm
from models import Category


class CategoriesView(FlaskView):
    route_base = '/categories'
    decorators = [login_required]

    def index(self):
        form = CategoryForm()
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        limit = 5
        categories, count = Category.pagination(page=page, limit=limit, desc=False)

        pagination = Pagination(page=page,
            per_page=limit,
            total=count,
            record_name=gettext('posts'),
            alignment='right',
            bs_version=3)
        trans = TranferCatForm()
        return render_template('admin/categories/index.html',
            title=gettext('Categories | %(page)s', page=page),
            form=form,
            categories=categories,
            pagination=pagination,
            trans=trans)

    @route('/transfer', methods=['POST'])
    def transfer_post(self):
        trans = TranferCatForm()
        if trans.validate_on_submit():
            cat_from = Category.get_by_id(trans.from_id.data)
            cat_to = Category.get_by_id(trans.to_id.data)
            
            if cat_from and cat_to:
                Category.transfer_posts(cat_from, cat_to)
                flash(gettext('The posts were transfered from %(from_name)s to %(to_name)s',
                    from_name=cat_from.name, to_name=cat_to.name))
            else:
                flash(gettext('Either category was not found'), 'error')
        else:
            flash(trans.get_errors(), 'error')

        return redirect(url_for('CategoriesView:index'))

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
                    return util.redirect_json_or_html(url_for('CategoriesView:index'), 'category')
                except:
                    flash(gettext('Error while creating the category'), 'error')
            else:
                flash(gettext('Invalid submission, please check the message below'), 'error')
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
                    return util.redirect_json_or_html(url_for('CategoriesView:index'), 'category')
                except:
                    return util.redirect_json_or_html(url_for('CategoriesView:index'), 'category', gettext('Error while updating the category'))
            else:
                if request.is_xhr:
                    return util.redirect_json_or_html(url_for('CategoriesView:index'), 'category', gettext('Invalid submission, please check the message below'))
                else:
                    flash(gettext('Invalid submission, please check the message below'), 'error')
        else:
            form = NewCategoryForm(category)
        return render_template('admin/categories/edit.html',
            title=gettext('Edit Category: %(name)s', name=category.name),
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
                return util.redirect_json_or_html(url_for('CategoriesView:index'),
                    'category',
                    gettext('Sorry, the last category can not be removed'))

            name = category.name
            Category.delete(category.id)
            flash(gettext('The category "%(name)s" was removed', name=name))
        except:
            return util.redirect_json_or_html(url_for('CategoriesView:index'),
                'category',
                gettext('Error while removing the category'))

        return util.redirect_json_or_html(url_for('CategoriesView:index'), 'category')
