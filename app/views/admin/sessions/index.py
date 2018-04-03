# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import gettext as _
from app.models import User
from app.helpers import send_registration_email, verify_captcha, render_view
from forms import LoginForm, SignUpForm
import datetime

mod = Blueprint('sessions', __name__)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_view(url_for('latest'),
                           redirect=True,
                           message=_('SESSIONS_MSG_ALREADY_SIGNED_IN'))

    form = LoginForm()
    if form.is_submitted():
        try:
            user = User.find_by_email(form.email.data)

            if not user or not user.check_password(form.password.data):
                raise Exception(_('SESSIONS_ERROR_LOGIN'))

            # Update the User's info
            user.last_login = user.last_seen
            user.last_seen = datetime.datetime.utcnow()
            user.save()

            redirect_to = session.pop('redirect_to', None)

            if not redirect_to:
                redirect_to = url_for('latest')

            remember = form.remember_me.data

            login_user(user, remember=remember)

            return render_view(redirect_to,
                               redirect=True,
                               message=_('SESSIONS_MSG_LOGIN_SUCESS'))

        except Exception as e:
            flash(e.message, 'error')

    return render_view('admin/sessions/signin.html',
                       form=form)


@mod.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()

    return render_view(url_for('latest'),
                       redirect=True,
                       message=_('SESSIONS_MSG_SIGNED_OUT'))


@mod.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return render_view(url_for('latest'),
                           redirect=True,
                           message=_('SESSIONS_MSG_ALREADY_SIGNED_IN'))

    form = SignUpForm()

    if form.is_submitted():
        try:
            if not form.validate():
                raise Exception(_('ERROR_INVALID_SUBMISSION'))

            if not verify_captcha():
                raise Exception(_('SESSIONS_ERROR_UNFINISHED_CHALLENGE_LBL'))

            # Create user from the form
            user = User.create()

            form.populate_obj(user)
            user.set_password(form.password.data)
            user.last_seen = datetime.datetime.utcnow()
            user.last_login = datetime.datetime.utcnow()

            # store the user
            user.save()

            # Login User
            login_user(user)

            # send registration email
            send_registration_email(user)

            return render_view(url_for('latest'),
                               redirect=True,
                               message=_('SESSIONS_MSG_SIGNUP_COMPLETED'))
        except Exception as e:
            flash(e.message, 'error')

    return render_view('admin/sessions/signup.html',
                       form=form)
