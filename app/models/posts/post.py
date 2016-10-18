# -*- coding: utf8 -*-

from flask.ext.login import current_user
from app import db
from app.utils.db import ModelBase, MutableDict
import datetime


class Post(db.Model, ModelBase):

  __tablename__ = 'posts'

  __json_meta__ = ['id', 'title', 'body', 'extra_body', 'user', 'cover_picture', 'category', 'anonymous']

  id = db.Column(db.Integer, primary_key=True)

  title = db.Column(db.String(255))
  user_id = db.Column(db.Integer, db.ForeignKey(
      'users.id', ondelete='CASCADE', onupdate='NO ACTION'))
  category_id = db.Column(db.Integer, db.ForeignKey(
      'categories.id', ondelete='CASCADE', onupdate='NO ACTION'))

  anonymous = db.Column(db.SmallInteger)
  attributes = db.Column(MutableDict.as_mutable(db.PickleType))

  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  modified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __repr__(self):  # pragma: no cover
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
  def cover_picture(self):
		from app.models import Picture
		return Picture.get_by_id(self.cover_picture_id)

  @property
  def cover_picture_id(self):
    return self.get_attribute('cover_picture_id', 0)

  @cover_picture_id.setter
  def cover_picture_id(self, value):
    return self.set_attribute('cover_picture_id', value)

  def is_mine(self):
    return current_user.is_authenticated and self.user.id == current_user.id

  def can_edit(self):
    return current_user.is_authenticated and (self.user.id == current_user.id or current_user.is_admin)

  @classmethod
  def posts_by_user(cls, user_id, limit=10, page=1, orderby='id', desc=True):
    query = cls.query.filter_by(user_id=user_id)
    count = query.count()
    records = []
    if count:
      sort_by = '%s %s' % (orderby, 'DESC' if desc else 'ASC')
      records = query.order_by(db.text(sort_by)).limit(
          limit).offset((page - 1) * limit)
    return records, count
