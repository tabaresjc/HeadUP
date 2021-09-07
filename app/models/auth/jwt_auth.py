# -*- coding: utf-8 -*-

from flask_login import UserMixin
from micawber.providers import InvalidJson
from app import sa
from app.models import Base
from app.helpers import ModelHelper
import config
import datetime
import jwt
import uuid


class JwtAuth(Base, sa.Model, ModelHelper, UserMixin):

    __tablename__ = 'jwt_auth'

    __json_meta__ = [
        'id',
        'user_id',
        'access_token',
        'user_token',
        'created_at',
        'refreshed_at'
    ]

    JWT_SHORT_LIVED_TYPE = 'SL'
    JWT_LONG_LIVED_TYPE = 'LL'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
                                                  ondelete='CASCADE',
                                                  onupdate='NO ACTION'))
    access_token = sa.Column(sa.String(127))
    user_token = sa.Column(sa.String(127))
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    refreshed_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    expired_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    user = sa.relationship('User', lazy="joined")

    def __init__(self, user_id, access_token=None, *args, **kwargs):
        super(JwtAuth, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.access_token = access_token if access_token else uuid.uuid4().hex
        self.user_token = uuid.uuid4().hex
        self.refreshed_at = datetime.datetime.utcnow()

        # set long/short lived tokens when access token is provided
        if access_token:
            self.expired_at = datetime.datetime.utcnow() + \
                datetime.timedelta(minutes=config.JWT_EXP_MINUTES)
        else:
            self.expired_at = datetime.datetime.utcnow() + \
                datetime.timedelta(days=config.JWT_EXP_DAYS)

    def sign_access_token(self):
        payload = {
            'is_authenticated': self.user.is_authenticated if self.user else False,
            'is_admin': self.user.is_admin if self.user else False,
            'refresh_token': self.refresh_token,
            'typ': self.JWT_LONG_LIVED_TYPE,
            'exp': self.expired_at,
            'iat': self.created_at
        }

        return JwtAuth.encode_token(payload)

    def sign_user_token(self):
        payload = {
            'is_authenticated': self.user.is_authenticated if self.user else False,
            'is_admin': self.user.is_admin if self.user else False,
            'user_token': self.user_token,
            'typ': self.JWT_SHORT_LIVED_TYPE,
            'exp': self.expired_at,
            'iat': self.created_at
        }

        return JwtAuth.encode_token(payload)

    @property
    def refresh_token(self):
        return '%s|%s' % (self.access_token, self.user_token)

    @classmethod
    def find_by_refresh_token(cls, refresh_token):
        access_token, user_token = refresh_token.split('|')
        return cls.query.filter_by(access_token=access_token, user_token=user_token).first()

    @classmethod
    def find_by_user_token(cls, user_token):
        return cls.query.filter_by(user_token=user_token).first()

    @classmethod
    def find_by_token(cls, token):
        data = cls.decode_token(token)

        if data.get('refresh_token'):
            return cls.find_by_refresh_token(data.get('refresh_token'))
        if data.get('user_token'):
            return cls.find_by_user_token(data.get('user_token'))

        raise ValueError('Invalid token, abort operation')

    @classmethod
    def revoke_access_token(cls, access_token):
        q = JwtAuth.__table__.delete() \
            .where(cls.access_token == access_token)
        cls.session_execute(q)
        cls.commit_transaction()

    @classmethod
    def decode_token(cls, token):
        return jwt.decode(token, config.JWT_SECRET_KEY)

    @classmethod
    def encode_token(cls, payload):
        return jwt.encode(payload, config.JWT_SECRET_KEY)
