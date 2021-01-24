# -*- coding: utf8 -*-

from flask import request, abort
from flask_login import current_user, login_required, login_user, logout_user
from flask_classy import FlaskView, route
from flask_babel import gettext as _
from app.helpers import render_json, render_json_template, send_email
from app.models import User, UserSession
from app import csrf, login_manager, campaign, logger
import datetime


class SessionsApiView(FlaskView):
    route_base = '/api/sessions'

    @csrf.exempt
    @route('/anonymous', methods=['POST'])
    def anonymous(self):
        if current_user.is_authenticated:
            logout_user()

        session = UserSession(None)
        session.save()

        return render_json(token=session.auth_token)

    @csrf.exempt
    @route('/signin', methods=['POST'])
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

        session = UserSession(user.id)
        session.save()

        return render_json(token=session.auth_token)

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
        if not login_manager.is_api_request:
            abort(400)

        logout_user()
        session = UserSession.find_by_auth_token(login_manager.auth_token)

        if session:
            session.remove()

        return render_json(status=204)

    @route('/logout', methods=['POST'])
    @login_required
    def logout(self):
        logout_user()

        return render_json(status=204)

    @csrf.exempt
    @route('/signup', methods=['POST'])
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

        session = UserSession(user.id)
        session.save()

        self.post_user_registration(user)

        return render_json(token=session.auth_token)

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
