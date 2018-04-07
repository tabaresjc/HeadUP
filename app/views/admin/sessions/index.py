# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import gettext as _
from app.models import User
from app.helpers import send_email, verify_captcha, render_view
from forms import LoginForm, SignUpForm, ForgotPasswordForm, ResetPasswordForm
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
                redirect_to = url_for('dashboard')

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
            send_email('registration', user)

            return render_view(url_for('latest'),
                               redirect=True,
                               message=_('SESSIONS_MSG_SIGNUP_COMPLETED'))
        except Exception as e:
            flash(e.message, 'error')

    return render_view('admin/sessions/signup.html',
                       form=form)


@mod.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return render_view(url_for('latest'),
                           redirect=True,
                           message=_('SESSIONS_MSG_ALREADY_SIGNED_IN'))

    form = ForgotPasswordForm()

    if form.is_submitted():
        try:
            if not form.validate():
                raise Exception(_('ERROR_INVALID_SUBMISSION'))

            email = form.email.data

            user = User.find_by_email(email)

            if not user:
                raise Exception(_('SESSIONS_ERROR_MAIL_NOT_FOUND', email=email))

            user.generate_reset_password()

            flash(_('SESSIONS_PASSWORD_RESET', email=email))

            return render_view(url_for('sessions.forgot_password'),
                               redirect=True)

        except Exception as e:
            flash(e.message, 'error')

    return render_view('admin/sessions/forgot_password.html',
                       form=form)


@mod.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return render_view(url_for('latest'),
                           redirect=True,
                           message=_('SESSIONS_MSG_ALREADY_SIGNED_IN'))

    code = request.values.get('code', None)
    user = User.find_by_reset_password_code(code)

    if not user:
        return render_view(url_for('sessions.forgot_password'),
                           redirect=True,
                           message=_('ERROR_INVALID_RESET_PASSWORD_CODE'))

    form = ResetPasswordForm(user=user)

    if form.is_submitted():
        try:
            if not form.validate():
                raise Exception(_('ERROR_INVALID_SUBMISSION'))

            user.set_password(form.password.data)
            user.reset_password = None

            # store the user
            user.save()

            # TODO: send reset password email

            return render_view(url_for('sessions.login'),
                               redirect=True,
                               message=_('SESSIONS_MSG_PASSWORD_RESET_COMPLETED'))

        except Exception as e:
            flash(e.message, 'error')

    return render_view('admin/sessions/reset_password.html',
                       form=form)
