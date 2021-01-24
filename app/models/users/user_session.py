# -*- coding: utf-8 -*-

from flask_login import UserMixin, current_user
from app import sa
from app.models import Base
from role import Role
from app.helpers import ModelHelper, MutableObject
import datetime
import uuid


class UserSession(Base, sa.Model, ModelHelper, UserMixin):

    __tablename__ = 'user_sessions'

    __json_meta__ = [
        'id',
        'user_id',
        'auth_token',
        'created_at',
        'refreshed_at'
    ]

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
                                                  ondelete='CASCADE',
                                                  onupdate='NO ACTION'))
    auth_token = sa.Column(sa.String(255))
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    refreshed_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    user = sa.relationship('User', lazy="joined")

    def __init__(self, user_id, *args, **kwargs):
        super(UserSession, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.auth_token = str(uuid.uuid1())

    def refresh(self):
        self.refreshed_at = datetime.datetime.utcnow()

    @classmethod
    def find_by_auth_token(cls, auth_token):
        return cls.query.filter_by(auth_token=auth_token).first()

    @classmethod
    def find_user_by_auth_token(cls, auth_token):
        user_session = cls.find_by_auth_token()

        if not user_session:
            return None

        return user_session.user
