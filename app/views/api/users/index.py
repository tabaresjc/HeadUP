# -*- coding: utf8 -*-

from flask import request, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Vote, User
from app import cache


class UsersApiView(FlaskView):
    route_base = '/api/users'

    @route('/profile', methods=['GET'])
    def profile(self):
        user = current_user._get_current_object()

        return render_json(user=user)
