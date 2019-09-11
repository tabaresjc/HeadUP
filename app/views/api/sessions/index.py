# -*- coding: utf8 -*-

from flask import request, abort
from flask_login import current_user, login_required, login_user, logout_user
from flask_classy import FlaskView, route
from flask_babel import gettext as _
from app.helpers import render_json
from app.models import User
import datetime


class SessionsApiView(FlaskView):
    route_base = '/api/sessions'

    @route('/login', methods=['POST'])
    def login(self):
        data = request.json

        if current_user.is_authenticated:
            logout_user()

        email = data.get('email', None)
        password = data.get('password', None)
        remember = data.get('remember', 0) != 0

        user = User.find_by_email(email)

        if not user or not user.check_password(password):
            abort(409, _('SESSIONS_ERROR_LOGIN'))

        # Update the User's info
        user.last_login = user.last_seen
        user.last_seen = datetime.datetime.utcnow()
        user.save()

        login_user(user, remember=remember)

        return render_json(user=user)

    @route('/logout', methods=['POST'])
    @login_required
    def logout(self):
        logout_user()

        return render_json(message=_('SESSIONS_MSG_SIGNED_OUT'))
