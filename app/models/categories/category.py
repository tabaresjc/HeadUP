# -*- coding: utf8 -*-

from flask_login import current_user
from app import db
from app.utils.db import ModelBase, MutableDict
import datetime


class Category(db.Model, ModelBase):

    __tablename__ = 'categories'

    __json_meta__ = ['id', 'name', 'slug']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    slug = db.Column(db.String(128), index=True, unique=True)
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
        return current_user and current_user.is_admin

    @classmethod
    def get_list(cls):
        return [(g.id, g.name) for g in cls.query.all()]

    @classmethod
    def transfer_posts(cls, from_category, to_category=None):
        from app.posts.models import Post
        result, count = cls.pagination(limit=1, desc=False)
        if count <= 1:
            return False
        if not to_category:
            to_category = result.one()

        Post.query.filter_by(category_id=from_category.id).update(
            dict(category_id=to_category.id))

        db.session.commit()
        return True

    @classmethod
    def get_by_cat_slug(cls, cat, slug):
        category = cls.query.filter_by(slug=cat).one_or_none()
        if not category:
            return None
        return category.posts

    @classmethod
    def get_by_cat(cls, cat):
        return cls.query.filter_by(slug=cat).one_or_none()

    @classmethod
    def get_posts_by_cat(cls, cat, limit=10, page=1, desc=True):
        category = cls.query.filter_by(slug=cat).one_or_none()
        if not category:
            return None, None
        posts = category.posts.order_by(db.text('id DESC')).limit(
            limit).offset((page - 1) * limit)
        return posts, category
