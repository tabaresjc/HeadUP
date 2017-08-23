# -*- coding: utf8 -*-

from flask_login import current_user
from app import db
from app.helpers import ModelHelper
from config import UPLOAD_MEDIA_PICTURES, UPLOAD_MEDIA_PICTURES_PATH
import datetime
import os


class Vote(db.Model, ModelHelper):

    __tablename__ = 'votes'
    __table_args__ = (
        db.Index('idx_object_user', 'object_kind', 'object_id', 'user_id'),
    )
    __json_meta__ = ['id', 'object_id', 'object_kind', 'user_id']

    id = db.Column(db.BigInteger, primary_key=True)

    object_id = db.Column(db.Integer)
    object_kind = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE', onupdate='NO ACTION'))

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):  # pragma: no cover
        return '<Vote %r>' % (self.id)
