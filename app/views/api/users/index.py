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

    @route('/stories/votes', methods=['GET'])
    @login_required
    def stories_votes(self):
        user = current_user._get_current_object()
        records = Vote.votes_by_user_id(user.id)
        votes = map(lambda x: x.target_id, records)
        return render_json(votes=votes)
