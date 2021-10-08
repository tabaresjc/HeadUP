# -*- coding: utf8 -*-

from werkzeug.exceptions import Unauthorized
from flask import request, abort
from flask_login import current_user, login_required, login_user, logout_user
from flask_classy import FlaskView, route
from flask_babel import gettext as _
from app.helpers import render_json, send_email
from app.models import User, AuthTokens
from app import csrf, login_manager, campaign, logger
import datetime


class SessionsApiView(FlaskView):
    route_base = '/api/sessions'

    @route('/anonymous', methods=['POST'])
    @csrf.exempt
    def anonymous(self):
        auth_token = AuthTokens(None)
        auth_token.save()

        return render_json(token=auth_token.sign_access_token(),
                           expired_at=auth_token.expired_at,
                           access_code=auth_token.access_code)

    @route('/signin', methods=['POST'])
    @csrf.exempt
    def signin(self):
        data = request.json
        email = data.get('email', None)
        password = data.get('password', None)

        if not User.is_valid_email(email):
            abort(409, 'USER_EMAIL_INVALID_ERROR')

        user = User.find_by_email(email)

        if not user or not user.check_password(password):
            abort(409, 'API_ERROR_SESSION_LOGIN')

        logout_user()

        # Update the User's info
        user.last_login = user.last_seen
        user.last_seen = datetime.datetime.utcnow()
        user.save()

        auth_token = AuthTokens(user.id)
        auth_token.save()

        return render_json(token=auth_token.sign_access_token(),
                           expired_at=auth_token.expired_at,
                           access_code=auth_token.access_code)

    @route('/refresh-token', methods=['POST'])
    @csrf.exempt
    def refresh_token(self):
        data = request.json
        token = data.get('token', None)
        access_code = data.get('access_code', None)

        try:
            if not access_code:
                raise Exception('Missing access code')

            auth_token = AuthTokens.find_by_token(token)

            if not auth_token:
                raise Exception('Token is invalid or expired')

            if auth_token.access_code != access_code:
                raise Exception('Token not found')

            AuthTokens.revoke_access_token(auth_token.access_token)

            new_auth_token = AuthTokens(auth_token.user_id)
            new_auth_token.save()

            return render_json(token=new_auth_token.sign_access_token(),
                               expired_at=new_auth_token.expired_at,
                               access_code=new_auth_token.access_code)
        except Exception as e:
            abort(401, e.message)

    @route('/login', methods=['POST'])
    def login(self):
        data = request.json

        email = data.get('email', None)
        password = data.get('password', None)
        remember = data.get('remember', 1) == 0

        if not User.is_valid_email(email):
            abort(409, 'USER_EMAIL_INVALID_ERROR')

        user = User.find_by_email(email)

        if not user or not user.check_password(password):
            abort(409, 'API_ERROR_SESSION_LOGIN')

        logout_user()

        # Update the User's info
        user.last_login = user.last_seen
        user.last_seen = datetime.datetime.utcnow()
        user.save()

        login_user(user, remember=remember)

        return render_json(user=user)

    @route('/signout', methods=['POST'])
    @login_required
    def signout(self):
        try:
            auth_token = AuthTokens.find_by_token(login_manager.jwt_token)

            if auth_token:
                AuthTokens.revoke_access_token(auth_token.access_token)

            return render_json(status=204)
        except Exception as e:
            abort(401, e.message)

    @route('/logout', methods=['POST'])
    @login_required
    def logout(self):
        logout_user()

        return render_json(status=204)

    @route('/signup', methods=['POST'])
    @csrf.exempt
    def signup(self):
        data = request.json
        email = data.get('email', None)
        nickname = data.get('nickname', None)
        password = data.get('password', None)

        if not User.is_valid_email(email):
            abort(409, 'USER_EMAIL_INVALID_ERROR')

        if not User.is_valid_nickname(nickname):
            abort(409, 'USER_NICKNAME_INVALID')

        if User.is_email_taken(email):
            abort(409, 'USER_EMAIL_TAKEN_ERROR')

        if User.is_nickname_taken(nickname):
            abort(409, 'USER_NICKNAME_TAKEN_ERROR')

        logout_user()

        user = User.create(email=email,
                           nickname=nickname,
                           last_seen=datetime.datetime.utcnow(),
                           last_login=datetime.datetime.utcnow())

        user.set_password(password)

        # store the user
        user.save()

        auth_token = AuthTokens(user.id)
        auth_token.save()

        self.post_user_registration(user)

        return render_json(token=auth_token.sign_access_token(),
                           expired_at=auth_token.expired_at,
                           access_code=auth_token.access_code)

    def post_user_registration(self, user):
        try:
            campaign.add_suscriber(user.email, user.nickname, '')

            # login user
            if not login_manager.is_api_request:
                login_user(user, remember=True)

            # send registration email
            send_email('registration', user)
        except Exception as e:
            logger.debug(e)
