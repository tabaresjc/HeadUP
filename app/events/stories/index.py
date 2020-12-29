# -*- coding: utf8 -*-

from app import socketio, app, cache
from flask_login import current_user
from app.models import Vote, Feed
from flask_socketio import emit


@socketio.on('vote_story', namespace='/')
def vote_post(message):
    target_id = int(message.get('target_id', 0))
    user_id = int(current_user.get_id() or 0)

    try:
        if not target_id:
            raise ValueError('ERROR_UNKNOWN_POST_ID')

        if not user_id:
            raise ValueError('ERROR_INVALID_USER')

        is_upvote, count = Vote.cast_vote(user_id,
                                          target_id,
                                          Vote.KIND_STORY)
        # clear related cache objects
        Feed.clear_cached_posts()

        data = {
            'target_id': target_id,
            'user_id': user_id,
            'count': count,
            'is_upvote': is_upvote
        }


        emit('vote_story_results', data, broadcast=True)

    except Exception as e:
        app.logger.error(
            u'[SocketIO] error on "vote" event, %s', e, exc_info=True)
