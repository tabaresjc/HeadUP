# -*- coding: utf8 -*-

from flask import flash, redirect, session, url_for, request, g, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_classy import FlaskView, route
from flask_babel import gettext as _, refresh
from flask_paginate import Pagination
from app.models import Post, User, Picture, Feed
from app.helpers import render_view
from forms import UserForm


class UsersView(FlaskView):
    route_base = '/mypage/users'
    decorators = [login_required]

    def index(self):
        page = request.values.get('page', 1, type=int)
        limit = 20
        users, total = User.pagination(page=page,
                                       limit=limit,
                                       orderby='users.id',
                                       desc=False)

        if not users.count() and page > 1:
            return render_view(url_for('UsersView:index_1'),
                               redirect=True)

        return render_view('admin/users/index.html',
                           users=users,
                           page=page,
                           limit=limit,
                           total=total)

    def get(self, id):
        user = User.get_by_id(id)

        if user is None or not user.can_edit():
            message = _('USER_NOT_FOUND')
            return render_view(url_for('UsersView:index'),
                               status=False,
                               redirect=True,
                               message=message)

        return render_view('admin/users/show.html', user=user)

    @route('/new', methods=['GET', 'POST'])
    def post(self):

        form = UserForm()

        if form.is_submitted():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                user = User.create()
                form.populate_obj(user)
                user.set_password(form.password.data)
                user.save()

                return render_view(url_for('UsersView:get', id=user.id),
                                   redirect=True,
                                   message=_('USER_CREATE_SUCCESS'))
            except Exception as e:
                flash(e.message, 'error')

        return render_view('admin/users/add.html', form=form, user=None)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        user = User.get_by_id(id)

        if user is None:
            return render_view(url_for('UsersView:index'),
                               status=False,
                               redirect=True,
                               message=_('USER_NOT_FOUND'))

        if not user.can_edit():
            abort(401)

        form = UserForm(user=user)

        if form.is_submitted():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                if form.password.data:
                    user.set_password(form.password.data)
                del form.password
                form.populate_obj(user)
                user.save()

                refresh()

                return render_view(url_for('UsersView:get', id=user.id),
                                   redirect=True,
                                   message=_('USER_SAVE_SUCCESS'))
            except Exception as e:
                flash(e.message, 'error')

        return render_view('admin/users/edit.html',
                           form=form,
                           user=user)

    @route('/remove/<int:id>', methods=['POST', 'DELETE'])
    def delete(self, id):

        user = User.get_by_id(id)

        if user is None:
            return render_view(url_for('UsersView:index'),
                               status=False,
                               redirect=True,
                               message=_('USER_NOT_FOUND'))

        if not user.can_edit():
            abort(401)

        try:
            if current_user.id == user.id:
                raise Exception('Can\'t remove your own account.')

            name = user.name
            User.delete(user.id)

            flash(_('USER_DELETE_SUCCESS', name=name))

        except Exception as e:
            flash(_('USER_DELETE_FAIL', error=e.message), 'error')

        return render_view(url_for('UsersView:index'),
                           redirect=True)

    @route('/<int:id>/upload-profile-picture/', methods=['POST'])
    def upload_profile_picture(self, id):
        user = User.get_by_id(id)

        f = request.files.get('file')

        if f:
            picture = Picture.create()
            picture.save_file(f, current_user)
            user.profile_picture_id = picture.id if picture else 0
            user.save()

        return render_view('', user=user)

    @route('/<int:id>/posts/', endpoint='user_post')
    def user_post(self, id):
        user = User.get_by_id(id)

        if user is None:
            return render_view(url_for('UsersView:index'),
                               status=False,
                               message=_('USER_NOT_FOUND'))

        limit = 10
        page = request.values.get('page', 1, type=int)

        posts, total = user.get_user_posts(page=page, limit=limit)

        return render_view("admin/users/user_posts.html",
                           user=user,
                           posts=posts,
                           page=page,
                           limit=limit,
                           total=total)

    @route('/<int:id>/stamp/hide/<int:stamp_id>', methods=['POST'])
    def hide_stamp(self, id, stamp_id):

        if not current_user.is_admin:
            abort(403)

        user = User.get_by_id(id)

        if user is None:
            abort(401)

        post = Post.get_by_id(stamp_id)

        if post is None:
            abort(401)

        try:
            if post.is_hidden:
                # unblock the post
                post.status = post.old_status
            else:
                # save current status and block the post
                post.old_status = post.status
                post.status = Post.POST_HIDDEN

            post.save()
            Feed.clear_feed_cache()

            if post.is_hidden:
                flash(_('USER_POST_HIDE_SUCCESS'))
            else:
                flash(_('USER_POST_RESTORE_SUCCESS'))

        except Exception as e:
            flash(_('USER_POST_HIDE_OR_RESTORE_FAIL', error=e.message), 'error')

        return render_view(url_for('UsersView:get', id=id),
                           redirect=True)

    @route('/<int:id>/send-email/<string:kind>', methods=['GET'])
    def send_email(self, id, kind):
        if not current_user.is_admin:
            abort(401)

        user = User.get_by_id(id)

        if kind == 'registration':
            from app.helpers.email.registration import send_registration_email
            send_registration_email(user)
        flash('done!')
        return render_view(url_for('UsersView:get', id=id), redirect=True)
