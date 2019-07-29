# -*- coding: utf8 -*-

from app import socketio
from flask_socketio import emit

@socketio.on('vote')
def vote(message):
    id = message.get('id', -1)
    vote = int(message.get('vote', 0)) + 1

    emit('vote_results', {'id': id, 'vote': vote}, broadcast=True)
