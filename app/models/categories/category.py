# -*- coding: utf8 -*-

from flask import url_for
from flask_login import current_user
from app import sa
from app.models import Base
from app.helpers import ModelHelper, MutableObject
import datetime


class Category(Base, sa.Model, ModelHelper):

    __tablename__ = 'categories'

    __json_meta__ = [
        'id',
        'name',
        'name_es',
        'name_fr',
        'name_ja',
        'name_cn',
        'slug',
        'url'
    ]

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128), index=True, unique=True)
    slug = sa.Column(sa.String(128), index=True, unique=True)
    posts = sa.relationship('Post', backref='category', lazy='dynamic')
    attr = sa.Column(MutableObject.get_column())

    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Category %s>' % (self.id)

    def get_lang_name_or_default(self, lang):
        if lang == 'en':
            return self.name

        return self.get_attribute('name_%s' % lang, self.name)

    def get_lang_description_or_default(self, lang):
        if lang == 'en':
            return self.description

        return self.get_attribute('description_%s' % lang, self.description)

    @property
    def description(self):
        return self.get_attribute('description', u'')

    @description.setter
    def description(self, value):
        return self.set_attribute('description', value)

    @property
    def name_es(self):
        return self.get_attribute('name_es', u'')

    @name_es.setter
    def name_es(self, value):
        return self.set_attribute('name_es', value)

    @property
    def description_es(self):
        return self.get_attribute('description_es', u'')

    @description_es.setter
    def description_es(self, value):
        return self.set_attribute('description_es', value)

    @property
    def name_fr(self):
        return self.get_attribute('name_fr', u'')

    @name_fr.setter
    def name_fr(self, value):
        return self.set_attribute('name_fr', value)

    @property
    def description_fr(self):
        return self.get_attribute('description_fr', u'')

    @description_fr.setter
    def description_fr(self, value):
        return self.set_attribute('description_fr', value)

    @property
    def name_ja(self):
        return self.get_attribute('name_ja', u'')

    @name_ja.setter
    def name_ja(self, value):
        return self.set_attribute('name_ja', value)

    @property
    def description_ja(self):
        return self.get_attribute('description_ja', u'')

    @description_ja.setter
    def description_ja(self, value):
        return self.set_attribute('description_ja', value)

    @property
    def name_cn(self):
        return self.get_attribute('name_cn', u'')

    @name_cn.setter
    def name_cn(self, value):
        return self.set_attribute('name_cn', value)

    @property
    def description_cn(self):
        return self.get_attribute('description_cn', u'')

    @description_cn.setter
    def description_cn(self, value):
        return self.set_attribute('description_cn', value)

    @property
    def url(self):
        if not hasattr(self, '_url'):
            self._url = url_for('story.category', slug=self.slug)
        return self._url

    def can_edit(self):
        return current_user and current_user.is_admin

    @classmethod
    def search(cls, limit=10, page=1, keyword=None, order_by='id', desc=True):
        keyword_fields = [
            cls.name,
            cls.slug
        ]

        return super(Category, cls).search(limit=limit,
                                           page=page,
                                           order_by=order_by,
                                           keyword=keyword,
                                           keyword_fields=keyword_fields,
                                           desc=desc)

    @classmethod
    def items(cls, orderby='id', desc=True):
        query = cls.query
        count = query.count()
        records = []
        if count:
            sort_by = '%s %s' % (orderby, 'DESC' if desc else 'ASC')
            records = query.order_by(sa.text(sort_by)).all()
        return records, count

    @classmethod
    def get_list(cls):
        return [(g.id, g.name) for g in cls.query.all()]

    @classmethod
    def transfer_posts(cls, from_category, to_category=None):
        from app.models import Post
        result, count = cls.pagination(limit=1, desc=False)
        if count <= 1:
            return False
        if not to_category:
            to_category = result.one()

        Post.query.filter_by(category_id=from_category.id).update(
            dict(category_id=to_category.id))

        sa.session.commit()
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
        posts = category.posts.order_by(sa.text('id DESC')).limit(
            limit).offset((page - 1) * limit)
        return posts, category

    @classmethod
    def urlify(cls, s):
        import re
        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]+", ' ', s)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", '-', s)

        return s.lower()
