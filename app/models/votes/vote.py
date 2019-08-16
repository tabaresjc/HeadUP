# -*- coding: utf-8 -*-

from flask_login import current_user
from app import sa
from app.models import Base, Post
from app.helpers import ModelHelper, MutableObject
from sqlalchemy import Index
import datetime
import re


class Vote(Base, sa.Model, ModelHelper):

    __tablename__ = 'votes'
    __table_args__ = (
        Index('idx_post_kind', 'target_id', 'kind'),
        Index('idx_user_kind', 'user_id', 'kind'),
    )
    __json_meta__ = [
        'user_id',
        'target_id',
        'kind',
        'created_at',
        'modified_at'
    ]

    KIND_POST = 1

    user_id = sa.Column(sa.Integer, primary_key=True)
    target_id = sa.Column(sa.Integer, primary_key=True)
    kind = sa.Column(sa.Integer)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def votes_by_user_id(cls, user_id, kind=KIND_POST):
        return cls.query.filter_by(user_id=user_id, kind=kind)

    @classmethod
    def get_target(cls, target_id, kind=KIND_POST):
        if cls.KIND_POST == kind:
            return Post.get(target_id)
        return None

    @classmethod
    def cast_vote(cls, user_id, target_id, kind=KIND_POST, commit=True):
        is_upvote, count = False, 0

        try:
            # create a new savepoint in db
            sa.session.begin_nested()

            target = cls.get_target(target_id, kind)

            if not target:
                raise Exception('ERROR_VOTE_TARGET_NOT_FOUND')

            count = cls.query \
                .filter_by(target_id=target_id, kind=kind) \
                .count()

            vote = cls.get((user_id, target_id))

            is_upvote = vote is None

            if is_upvote:
                vote = cls.create(user_id=user_id,
                                  target_id=target_id,
                                  kind=kind)
                vote.save(commit=False)
                count += 1
            else:
                vote.remove(commit=False)
                count -= 1

            target.likes = count if count > -1 else 0
            target.save(commit=False)

            # commit fpr the current savepoint in db
            sa.session.commit()
        except Exception as e:
            # rollbank from the current savepoint in db
            sa.session.rollback()
            raise e

        if commit:
            sa.session.commit()

        return is_upvote, count
