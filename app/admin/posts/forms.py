# -*- coding: utf8 -*-

from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, BooleanField, SelectField, HiddenField, validators
from flask.ext.babel import lazy_gettext, gettext
from app.models import Category, Post


class PostForm(Form):
    title = TextField(lazy_gettext('Title'), [validators.Required()])
    body = TextAreaField(lazy_gettext('Your Challenge'), [validators.Required()])
    extra_body = TextAreaField(lazy_gettext(
        'Your Solution'), [validators.Required()])
    category_id = SelectField(u'Category', coerce=int)
    anonymous = BooleanField(lazy_gettext('Anonymous'), default=0)
    remain = BooleanField(lazy_gettext('Show Post'), default=False)
    cover_picture_id = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.category_id.data = 1
        self.category_id.choices = Category.get_list()

    def validate(self):
        if not Form.validate(self):
            return False
        return True


class EditPostForm(Form):
    title = TextField(lazy_gettext('Title'), [validators.Required()])
    body = TextAreaField(lazy_gettext('Your Challenge'), [validators.Required()])
    extra_body = TextAreaField(lazy_gettext(
        'Your Solution'), [validators.Required()])
    category_id = SelectField(u'Category', coerce=int)
    anonymous = BooleanField(lazy_gettext('Anonymous'), default=0)
    remain = BooleanField(lazy_gettext('Show Post'), default=False)
    cover_picture_id = HiddenField()

    def __init__(self, post, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.id = kwargs.get('id') if kwargs.get('id') else 0
        self.title.data = post.title
        self.body.data = post.body
        self.extra_body.data = post.extra_body
        self.anonymous.data = post.anonymous
        self.category_id.data = post.category_id
            self.cover_picture_id.data = post.cover_picture_id
        self.category_id.choices = Category.get_list()

    def validate(self):
        if not Form.validate(self):
            return False
        return True
