# -*- coding: utf8 -*-

from flask.ext.login import current_user
from app import db
from app.utils.db import ModelBase
from app.users.models import User, Role
import datetime


class Post(db.Model, ModelBase):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='NO ACTION'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE', onupdate='NO ACTION'))

    anonymous = db.Column(db.SmallInteger)
    attributes = db.Column(db.PickleType)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self): # pragma: no cover
      return '<Post %r>' % (self.title)

    @property
    def body(self):
        return self.get_attribute('body')

    @body.setter
    def body(self, value):
        return self.set_attribute('body', value)

    @property
    def extra_body(self):
        return self.get_attribute('extra_body')

    @extra_body.setter
    def extra_body(self, value):
        return self.set_attribute('extra_body', value)

    @property
    def image_url(self):
        return self.get_attribute('image_url', '')

    @image_url.setter
    def image_url(self, value):
        return self.set_attribute('image_url', value)

    def is_mine(self):
      return current_user.is_authenticated and self.user.id == current_user.id

    def can_edit(self):
      return current_user.is_authenticated and (self.user.id == current_user.id or current_user.is_admin())
