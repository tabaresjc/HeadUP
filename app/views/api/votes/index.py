# -*- coding: utf8 -*-

from flask import request, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from flask_socketio import emit
from app.helpers import render_json
from app.models import Vote, Post
from app import cache


class VotesApiView(FlaskView):
    route_base = '/api/votes'

    @login_required
    def post(self):
        data = request.json

        target = data.get('target')

        if target == 'story':
            return self._story_vote(data)

        abort(409, 'API_ERROR_INVALID_REQUEST_TYPE')

    def _story_vote(self, data):
        target_id = int(data.get('target_id', 0))
        user_id = int(current_user.get_id() or 0)

        if not user_id:
            abort(409, 'API_ERROR_INVALID_USER')

        if not target_id:
            abort(409, 'API_ERROR_INVALID_STORY_ID')

        story = Post.get_by_id(target_id)

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        is_upvote, count = Vote.cast_vote(current_user.id,
                                          target_id,
                                          Vote.KIND_STORY)

        vote = {
            'target': data.get('target'),
            'target_id': target_id,
            'user_id': current_user.id,
            'count': count,
            'is_upvote': is_upvote
        }

        emit('vote_story_results', vote, broadcast=True)

        return render_json(vote=vote)
