# -*- coding: utf8 -*-

from flask_login import current_user
from app.helpers import ModelHelper
from config import UPLOAD_MEDIA_PICTURES, UPLOAD_MEDIA_PICTURES_PATH
from app import sa
import datetime
import os



class Vote(sa.Model, ModelHelper):

    __tablename__ = 'votes'
    __table_args__ = (
        sa.Index('idx_object_user', 'object_kind', 'object_id', 'user_id'),
    )
    __json_meta__ = ['id', 'object_id', 'object_kind', 'user_id']

    id = sa.Column(sa.BigInteger, primary_key=True)

    object_id = sa.Column(sa.Integer)
    object_kind = sa.Column(sa.Integer)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
                                                  ondelete='CASCADE',
                                                  onupdate='NO ACTION'))
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):  # pragma: no cover
        return '<Vote %r>' % (self.id)
