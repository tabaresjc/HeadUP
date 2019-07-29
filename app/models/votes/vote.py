# -*- coding: utf-8 -*-

from flask_login import current_user
from app import sa
from app.models import Base
from app.helpers import ModelHelper, MutableObject
from sqlalchemy import Index
import datetime
import re


class Vote(Base, sa.Model, ModelHelper):

    __tablename__ = 'votes'
    __table_args__ = (
        Index('idx_post_kind', 'post_id', 'kind'),
        Index('idx_user_kind', 'user_id', 'kind'),
    )
    __json_meta__ = [
        'user_id',
        'post_id'
    ]

    KIND_POST = 1

    user_id = sa.Column(sa.Integer, primary_key=True)
    post_id = sa.Column(sa.Integer, primary_key=True)
    kind = sa.Column(sa.Integer)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def count_by_post(self):
        pass
