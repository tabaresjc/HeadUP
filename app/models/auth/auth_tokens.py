# -*- coding: utf-8 -*-

from flask import request
from flask_login import UserMixin
from micawber.providers import InvalidJson
from random import randint
from app import sa
from app.models import Base
from app.helpers import ModelHelper
import config
import datetime
import jwt
import uuid


class AuthTokens(Base, sa.Model, ModelHelper, UserMixin):

    __tablename__ = 'auth_tokens'

    __json_meta__ = [
        'id',
        'user_id',
        'access_token',
        'access_code',
        'created_at',
        'expired_at'
    ]

    JWT_SHORT_LIVED_TYPE = 'SL'
    JWT_LONG_LIVED_TYPE = 'LL'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
                                                  ondelete='CASCADE',
                                                  onupdate='NO ACTION'))
    access_token = sa.Column(sa.String(127))
    access_code = sa.Column(sa.String(63))
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    expired_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    user = sa.relationship('User', lazy="joined")

    def __init__(self, user_id, *args, **kwargs):
        super(AuthTokens, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.access_token = uuid.uuid4().hex
        self.access_code = ''.join(
            ["{}".format(randint(0, 9)) for num in range(0, 10)])
        self.expired_at = datetime.datetime.utcnow() + \
            datetime.timedelta(days=config.JWT_EXP_DAYS)

    def sign_access_token(self):
        payload = {
            'iss': request.host,
            'is_authenticated': self.user.is_authenticated if self.user else False,
            'is_admin': self.user.is_admin if self.user else False,
            'jti': self.access_token,
            'token_type': 'Bearer',
            'exp': self.expired_at,
            'iat': self.created_at
        }

        return AuthTokens.encode_token(payload)

    def get_user(self):
        if not self.user_id:
            return None
        return self.user

    @classmethod
    def find_by_token(cls, token):
        data = cls.decode_token(token)

        access_token = data.get('jti')

        if not access_token:
            raise ValueError('Invalid token, abort operation')

        return cls.query.filter_by(access_token=access_token).first()

    @classmethod
    def revoke_access_token(cls, access_token):
        q = AuthTokens.__table__.delete() \
            .where(cls.access_token == access_token)
        cls.session_execute(q)

    @classmethod
    def decode_token(cls, token):
        return jwt.decode(token, config.JWT_SECRET_KEY)

    @classmethod
    def encode_token(cls, payload):
        return jwt.encode(payload, config.JWT_SECRET_KEY)
