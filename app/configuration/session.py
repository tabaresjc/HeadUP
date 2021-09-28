# -*- coding: utf8 -*-

import datetime
from flask import request, session, flash, redirect, url_for, jsonify
from flask_babel import lazy_gettext as _lg
from werkzeug.exceptions import abort
from app.models import User, GuestUser, AuthTokens
from app.helpers import render_json
from app import login_manager
import app
import jwt
import config

# add our view as the login view to finish configuring the LoginManager
login_manager.login_view = "sessions.login"
login_manager.login_message = _lg('APP_LOGIN_WARNING_MESSAGE')
login_manager.anonymous_user = GuestUser


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@login_manager.request_loader
def load_user_from_request(request):
    try:
        token = login_manager.jwt_token

        if not token:
            return None

        auth_token = AuthTokens.find_by_token(token)

        if not auth_token:
            return None

        return auth_token.get_user()
    except jwt.exceptions.PyJWTError as e:
        return None


@login_manager.unauthorized_handler
def unauthorized():
    if login_manager.is_api_request:
        return render_json(_lg('ACCESS_DENIED'), 403)
    session['redirect_to'] = request.url
    flash(_lg('APP_SIGNIN_WARNING_MESSAGE'), 'error')
    return redirect(url_for('sessions.login'))


@app.app.before_request
def check_csrf():
    if not login_manager.is_api_request:
        app.csrf.protect()
