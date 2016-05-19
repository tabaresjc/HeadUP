# -*- coding: utf8 -*-

from flask.ext.login import current_user
from app import db
from app.utils.db import ModelBase, MutableDict
from app.posts.models import Post
import datetime


class Category(db.Model, ModelBase):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True)
    slug = db.Column(db.String(255), index=True, unique=True)
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    attributes = db.Column(MutableDict.as_mutable(db.PickleType))

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
      return '<Category %s>' % (self.id)

    @property
    def description(self):
        return self.get_attribute('description', u'')

    @description.setter
    def description(self, value):
        return self.set_attribute('description', value)

    def can_edit(self):
      return current_user and current_user.is_admin()

    @classmethod
    def get_list(cls):
      return [(g.id, g.name) for g in cls.query.all()]

    @classmethod
    def transfer_posts(cls, from_category, to_category=None):
      result, count = cls.pagination(limit=1, desc=False)
      if count <= 1:
        return False
      if not to_category:
        to_category = result.one()
      store.find(Post, Post.category_id == from_category.id).set(category_id=to_category.id)
      store.commit()
      return True

    @classmethod
    def get_by_cat_slug(cls, cat, slug):
      return store.find(Category,
        Category.slug == unicode(cat)).one().posts.find(Post.slug == unicode(slug)).one()

    @classmethod
    def get_by_cat(cls, cat):
      return store.find(Category, Category.slug == unicode(cat)).one()

    @classmethod
    def get_posts_by_cat(cls, cat, limit=10, page=1, desc=True):
      category = store.find(Category, Category.slug == unicode(cat)).one()
      offset = (page - 1) * limit
      bounderie = offset + limit
      return category.posts.find()[offset:bounderie], category
