# -*- coding: utf8 -*-

from flask import request, session, flash, redirect, url_for
from flask_babel import lazy_gettext as _lg

from app.models import User, UserSession, GuestUser
from app import login_manager
import app
import config

# add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "sessions.login"
login_manager.login_message = _lg('APP_LOGIN_WARNING_MESSAGE')
login_manager.anonymous_user = GuestUser


@login_manager.user_loader
def load_user(userid):
    return User.get_by_id(userid)


@login_manager.request_loader
def load_user_from_request(request):
    if not login_manager.is_api_request:
        return None

    auth_token = request.headers.get(config.SESSION_AUTH_TOKEN_NAME)

    if auth_token is None:
        return None

    user_session = UserSession.query \
        .filter_by(auth_token=auth_token) \
        .first()

    if not user_session or not user_session.user:
        return None

    user_session.refresh()
    user_session.save()

    return user_session.user


@login_manager.unauthorized_handler
def unauthorized():
    session['redirect_to'] = request.url
    flash(_lg('APP_SIGNIN_WARNING_MESSAGE'), 'error')
    return redirect(url_for('sessions.login'))


@app.app.before_request
def check_csrf():
    if not login_manager.is_api_request:
        app.csrf.protect()
