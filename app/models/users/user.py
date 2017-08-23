# -*- coding: utf-8 -*-

from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .role import Role
from app.helpers import ModelHelper, MutableObject
from hashlib import md5
import datetime
import re


class User(db.Model, ModelHelper, UserMixin):

    __tablename__ = 'users'

    __json_meta__ = ['id', 'email', 'nickname',
                     'is_admin', 'profile_picture_url']

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(128), index=True, unique=True)
    nickname = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(128))
    role_id = db.Column(db.Integer)
    attr = db.Column(MutableObject.get_column())

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __repr__(self):  # pragma: no cover
        return u'<User %s>' % (self.id)

    @property
    def name(self):
        return self.get_attribute('name', '')

    @name.setter
    def name(self, value):
        return self.set_attribute('name', value)

    @property
    def description(self):
        return self.get_attribute('description', '')

    @description.setter
    def description(self, value):
        return self.set_attribute('description', value)

    @property
    def nickname(self):
        return self.get_attribute('nickname')

    @nickname.setter
    def nickname(self, value):
        return self.set_attribute('nickname', value)

    @property
    def address(self):
        return self.get_attribute('address', '')

    @address.setter
    def address(self, value):
        return self.set_attribute('address', value)

    @property
    def phone(self):
        return self.get_attribute('phone', '')

    @phone.setter
    def phone(self, value):
        return self.set_attribute('phone', value)

    @property
    def last_seen(self):
        return self.get_attribute('last_seen')

    @last_seen.setter
    def last_seen(self, value):
        return self.set_attribute('last_seen', value)

    @property
    def last_login(self):
        return self.get_attribute('last_login')

    @last_login.setter
    def last_login(self, value):
        return self.set_attribute('last_login', value)

    @property
    def timezone(self):
        return self.get_attribute('timezone')

    @timezone.setter
    def timezone(self, value):
        return self.set_attribute('timezone', value)

    @property
    def lang(self):
        return self.get_attribute('lang')

    @lang.setter
    def lang(self, value):
        return self.set_attribute('lang', value)

    @property
    def profile_picture_id(self):
        return self.get_attribute('profile_picture_id')

    @profile_picture_id.setter
    def profile_picture_id(self, value):
        return self.set_attribute('profile_picture_id', value)

    @property
    def profile_picture(self):
        if not self.profile_picture_id:
            return None
        from app.models import Picture
        return Picture.get_by_id(self.profile_picture_id)

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.image_url
        return ''

    @property
    def role_desc(self):
        return Role.ROLES.get(self.role_id, '')

    def set_password(self, password):
        self.password = unicode(generate_password_hash(password))

    def check_password(self, password):
        return check_password_hash(str(self.password), str(password))

    @property
    def is_admin(self):
        return self.role_id == Role.ROLE_ADMIN

    @property
    def is_current(self):
        return self.id == current_user.id

    def can_edit(self):
        return self.id == current_user.id or current_user.is_admin

    def get_user_posts(self, limit=10, page=1):
        total = self.posts.count()
        posts = self.posts.order_by(db.text("id DESC")).offset(
            (page - 1) * limit).limit(limit)
        return posts, total

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def make_valid_name(cls, name):
        return re.sub('[!#\[\]\(\)\.]', '', name)

    @classmethod
    def make_valid_nickname(cls, nickname):
        return re.sub('[!#\[\]\(\)\.]', '', nickname)

    @classmethod
    def is_email_taken(cls, email):
        if cls.query.filter_by(email=email).count() > 0:
            return True
        else:
            return False

    @classmethod
    def is_nickname_taken(cls, nickname):
        if cls.query.filter_by(nickname=nickname).count() > 0:
            return True
        else:
            return False
