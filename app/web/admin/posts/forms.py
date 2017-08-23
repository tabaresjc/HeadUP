# -*- coding: utf8 -*-

from flask_wtf import Form
from wtforms import TextAreaField, TextField, BooleanField, SelectField, HiddenField, validators
from flask_babel import lazy_gettext, gettext
from app.models import Category, Post


class PostForm(Form):
    title = TextField(lazy_gettext('Title'), [validators.Required()])
    body = TextAreaField(lazy_gettext('Your Challenge'),
                         [validators.Required()])
    extra_body = TextAreaField(lazy_gettext(
        'Your Solution'), [validators.Required()])
    category_id = SelectField(u'Category', coerce=int)
    anonymous = BooleanField(lazy_gettext('Anonymous'), default=0)
    remain = BooleanField(lazy_gettext('Show Post'), default=False)
    cover_picture_id = HiddenField()
    editor_version = HiddenField()

    def __init__(self, post=None, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.category_id.choices = Category.get_list()
        if post:
            self.id = kwargs.get('id') if kwargs.get('id') else 0
            self.title.data = post.title
            self.body.data = post.body
            self.extra_body.data = post.extra_body
            self.anonymous.data = post.anonymous
            self.category_id.data = post.category_id
            self.cover_picture_id.data = post.cover_picture_id
            self.editor_version.data = post.editor_version
