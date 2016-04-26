# -*- coding: utf8 -*-

from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form
from flask.ext.babel import lazy_gettext, gettext, refresh
from app import app, login_manager
from flask.ext.paginate import Pagination
from models import User
from forms import UserForm, EditUserForm, NewUserForm
from app.posts.models import Post


class UsersView(FlaskView):
    route_base = '/users'
    decorators = [login_required]

    def index(self):
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        limit = 5
        users, count = User.pagination(page=page, limit=limit, orderby='users.id', desc=False)

        pagination = Pagination(page=page,
            per_page=limit,
            total= count,
            record_name=gettext('users'),
            bs_version=3)

        return render_template('admin/users/index.html',
            title = gettext('Users | Page %(page)s', page=page),
            users = users,
            pagination = pagination)

    def get(self,id):
        user = User.get_by_id(id)
        if user is None:
            flash(gettext('The user was not found'), 'error')
            return redirect(url_for('UsersView:index'))

        return render_template('admin/users/show.html',
            title = gettext('User\'s Profile | %(name)s', name=user.name),
            user = user)

    @route('/', methods = ['POST'])
    @route('/new', methods = ['GET'])
    def post(self):
        if request.method == 'POST':
            form = NewUserForm()
            if form.validate_on_submit():
                try:
                    user = User.create()
                    # Set Permissions
                    if current_user.is_admin():
                        user.role = int(form.role.data)

                    del form.role
                    del form.timezone
                    del form.lang
                    form.populate_obj(user)
                    user.set_password(form.password.data)
                    user.save()

                    flash(gettext('User was succesfully saved'))
                    return redirect(url_for('UsersView:get',id=user.id))
                except:
                    flash(gettext('Error while creating the user'), 'error')
                    raise
            else:
                flash(gettext('Invalid submission, please check the messages below'), 'error')
        else:
            form = NewUserForm()

        return render_template('admin/users/add.html',
            title = gettext('Create new user'),
            form = form,
            user = [])

    @route('/<int:id>', methods = ['PUT'])
    @route('/edit/<int:id>', methods = ['GET', 'POST'])
    def put(self, id):
        if not current_user.is_admin() and current_user.id != id:
            abort(401)

        user = User.get_by_id(id)
        if user is None:
            flash(gettext('The user was not found'), 'error')
            return redirect(url_for('UsersView:index'))

        if request.method in ['POST','PUT']:
            form = UserForm()
            if form.validate_on_submit():
                try:
                    if form.role_id.data != u'None':
                        user.role_id = int(form.role_id.data)
                    del form.role_id
                    if form.password.data:
                        user.set_password(form.password.data)
                    del form.password
                    user.phone = form.phone.data
                    form.populate_obj(user)
                    user.save()
                    refresh()
                    flash(gettext('User was succesfully saved' + user.phone))
                    if request.method == 'POST':
                        return redirect(url_for('UsersView:get', id=user.id))
                except:
                    flash(gettext('Error while updating the user'), 'error')
            else:
                flash(gettext('Invalid submission, please check the messages below'), 'error')

            if request.method == 'PUT':
                return jsonify(redirect_to=url_for('UsersView:index'))
        else:
            form = EditUserForm(user)
        return render_template('admin/users/edit.html',
            title = gettext('Edit User\'s Profile | %(name)s', name=user.name),
            form = form,
            user = user)

    @route('/<int:id>', methods = ['DELETE'])
    @route('/remove/<int:id>', methods = ['POST'])
    def delete(self,id):
        if not current_user.is_admin() and current_user.id != id:
            abort(401)
        if User.count() <= 1:
            abort(403)

        user = User.get_by_id(id)
        try:
            if user is None:
                raise Exception(gettext('User not found'))
            name  = user.name
            User.delete(user.id)
            flash(gettext('The user "%(name)s" was removed', name=name))
        except:
            flash(gettext('Error while removing the user'), 'error')

        if request.method == 'POST':
            return redirect(url_for('UsersView:index'))
        return jsonify(redirect_to=url_for('UsersView:index'))


    @route('/<int:id>/posts/', endpoint='user_post')
    def user_post(self,id):
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        user = User.get_by_id(id)
        if user is None:
            flash(gettext('The user was not found'), 'error')
            return redirect(url_for('UsersView:index'))

        limit = 5
        posts = user.get_user_posts(page=page, limit=limit)

        pagination = Pagination(page=page,
            per_page= limit,
            total= user.posts.count(),
            record_name= gettext('posts'),
            alignment = 'right',
            bs_version= 3)

        return render_template("admin/users/user_posts.html",
            title = gettext('User\'s Posts | %(name)s', name=user.name),
            user = user,
            posts = posts,
            pagination = pagination)
