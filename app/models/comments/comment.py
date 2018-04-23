# -*- coding: utf8 -*-

from flask_login import current_user
from app import sa
from app.models import Base
from app.helpers import ModelHelper, MutableObject
import datetime


class Comment(Base, sa.Model, ModelHelper):

    __tablename__ = 'comments'

    __json_meta__ = ['id', 'text', 'created_at', 'modified_at']

    id = sa.Column(sa.Integer, primary_key=True)
    post_id = sa.Column(sa.Integer,
                        sa.ForeignKey('posts.id',
                                      ondelete='CASCADE',
                                      onupdate='NO ACTION'))
    user_id = sa.Column(sa.Integer,
                        sa.ForeignKey('users.id',
                                      ondelete='CASCADE',
                                      onupdate='NO ACTION'))

    comment_id = sa.Column(sa.Integer, default=0, index=True, nullable=False)
    text = sa.Column(sa.Text)

    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Comment %s>' % (self.id)

    @property
    def parent_comment(self):
        if not self.comment_id:
            return None
        if not hasattr(self, '_parent_comment'):
            self._parent_comment = Comment.get_by_id(self.comment_id)
        return self._parent_comment

    @property
    def can_edit(self):
        from flask_login import current_user
        return (current_user.is_authenticated and
                (self.user.id == current_user.id or current_user.is_admin))

    @property
    def can_delete(self):
        from flask_login import current_user
        return (current_user.is_authenticated and
                (self.user_id == current_user.id or
                 self.post.user_id == current_user.id or
                 current_user.is_admin))
