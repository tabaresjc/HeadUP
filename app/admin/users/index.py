# -*- coding: utf8 -*-

from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_classy import FlaskView, route
from flask_wtf import Form
from flask_babel import lazy_gettext, gettext, refresh
from app import app, login_manager
from flask_paginate import Pagination
from app.models import Post, User, Picture
from app.utils.response import resp
from forms import EditUserForm, NewUserForm


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
        return resp('admin/users/index.html',
                    users=users,
                    page=page,
                    limit=limit,
                    total=total)

    def get(self, id):
        user = User.get_by_id(id)

        if user is None or not user.can_edit():
            return resp(url_for('UsersView:index'), status=False, redirect=True,
                        message=gettext('The requested user was not found'))

        return resp('admin/users/show.html', user=user)

    @route('/new', methods=['GET', 'POST'])
    def post(self):
        form = NewUserForm()

        if request.method == 'POST':

            if form.validate_on_submit():
                user = User.create()
                form.populate_obj(user)
                user.set_password(form.password.data)
                user.save()

                return resp(url_for('UsersView:get', id=user.id), redirect=True,
                            message=gettext('User was succesfully saved'))
            else:
                return resp('admin/users/add.html', form=form, user=None, status=False,
                            message=gettext('Invalid submission, please check the messages below'))

        return resp('admin/users/add.html', form=form, user=None)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        user = User.get_by_id(id)

        if user is None or not user.can_edit():
            flash(gettext('The user was not found'), 'error')
            return redirect(url_for('UsersView:index'))

        if request.method in ['POST']:
            form = EditUserForm()
            if form.validate_on_submit():
                if form.password.data:
                    user.set_password(form.password.data)
                del form.password
                form.populate_obj(user)
                user.save()
                refresh()
                return resp(url_for('UsersView:get', id=user.id), redirect=True,
                            message=gettext('User was succesfully updated'))
            else:
                return resp('admin/users/edit.html', form=form, user=user,
                            message=gettext('Invalid submission, please check the messages below'))
        else:
            form = EditUserForm(user=user)

        return resp('admin/users/edit.html', form=form, user=user)

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
            return resp(url_for('UsersView:index'), redirect=True,
                        message=gettext('The user "%(name)s" was removed', name=name))
        except Exception as e:
            return resp(url_for('UsersView:index'), redirect=True,
                        message=gettext('Error while removing the user, %(error)s', error=e))

    @route('/<int:id>/upload-profile-picture/', methods=['POST'])
    def upload_profile_picture(self, id):
        user = User.get_by_id(id)

        f = request.files.get('file')

        if f:
            picture = Picture.create()
            picture.save_file(f, current_user)
            user.profile_picture_id = picture.id if picture else 0
            user.save()

        return resp('', user=user)

    @route('/<int:id>/posts/', endpoint='user_post')
    def user_post(self, id):
        user = User.get_by_id(id)

        if user is None:
            return resp(url_for('UsersView:index'), status=False,
                        message=gettext('The user was not found'))

        page = request.values.get('page', 1, type=int)
        limit = 10

        posts, total = user.get_user_posts(page=page, limit=limit)

        return resp("admin/users/user_posts.html",
                    user=user,
                    posts=posts,
                    page=page,
                    limit=limit,
                    total=total)
