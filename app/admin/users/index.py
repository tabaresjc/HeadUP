# -*- coding: utf8 -*-

from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form
from flask.ext.babel import lazy_gettext, gettext, refresh
from app import app, login_manager
from flask.ext.paginate import Pagination
from app.models import Post, User
from forms import UserForm, EditUserForm


class UsersView(FlaskView):
    route_base = '/mypage/users'
    decorators = [login_required]

    def index(self):
        page = request.values.get('page', 1, type=int)
        limit = 20
        users, total = User.pagination(page=page, limit=limit,
                                       orderby='users.id', desc=False)
        if not users.count() and page > 1:
            return redirect(url_for('UsersView:index_1'))
        return render_template('admin/users/index.html',
                               users=users,
                               page=page,
                               limit=limit,
                               total=total)

    def get(self, id):
        user = User.get_by_id(id)

        if user is None or not user.can_edit():
            flash(gettext('The user was not found'), 'error')
            return redirect(url_for('UsersView:index'))

        return render_template('admin/users/show.html', user=user)

    @route('/new', methods=['GET', 'POST'])
    def post(self):
        form = UserForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                user = User.create()
                form.populate_obj(user)
                user.set_password(form.password.data)
                user.save()

                flash(gettext('User was succesfully saved'))
                return redirect(url_for('UsersView:get', id=user.id))
            else:
                flash(gettext('Invalid submission, please check the messages below'), 'error')

        return render_template('admin/users/add.html', form=form, user=None)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        user = User.get_by_id(id)

        if user is None or not user.can_edit():
            flash(gettext('The user was not found'), 'error')
            return redirect(url_for('UsersView:index'))

        form = EditUserForm(user)
        if request.method in ['POST']:
            if form.validate_on_submit():
                if form.password.data:
                    user.set_password(form.password.data)
                del form.password
                form.populate_obj(user)
                user.save()
                refresh()
                flash(gettext('User was succesfully saved'))
                return redirect(url_for('UsersView:get', id=user.id))
            else:
                flash(gettext('Invalid submission, please check the messages below'), 'error')

        return render_template('admin/users/edit.html', form=form, user=user)

    @route('/remove/<int:id>', methods=['POST', 'DELETE'])
    def delete(self, id):

        user = User.get_by_id(id)

        if user is None or not user.can_edit():
            abort(401)

        if current_user.id == user.id:
            abort(403)

        try:
            name = user.name
            User.delete(user.id)
            flash(gettext('The user "%(name)s" was removed', name=name))
        except Exception as e:
            flash(gettext('Error while removing the user, %(error)s', error=e), 'error')

        return redirect(url_for('UsersView:index'))

    @route('/<int:id>/posts/', endpoint='user_post')
    def user_post(self, id):
        user = User.get_by_id(id)

        if user is None:
            flash(gettext('The user was not found'), 'error')
            return redirect(url_for('UsersView:index'))

        page = request.values.get('page', 1, type=int)
        limit = 10

        posts, total = user.get_user_posts(page=page, limit=limit)

        return render_template("admin/users/user_posts.html",
                               user=user,
                               posts=posts,
                               page=page,
                               limit=limit,
                               total=total)
