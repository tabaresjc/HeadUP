# -*- coding: utf8 -*-

from flask_wtf import Form
from wtforms import TextAreaField, TextField, BooleanField, SelectField, HiddenField, validators
from flask_babel import lazy_gettext, gettext
from app.models import Category, Post


class PostForm(Form):

    title = TextField(lazy_gettext('Title'),
                      [validators.Required()])

    body = TextAreaField(lazy_gettext('Your Challenge'),
                         [validators.Required()])

    extra_body = TextAreaField(lazy_gettext('Your Solution'),
                               [validators.Required()])

    category_id = SelectField(u'Category', coerce=int)

    status = SelectField(u'Status', coerce=int)

    anonymous = BooleanField(lazy_gettext('Anonymous'), default=0)

    remain = BooleanField(lazy_gettext('Show Post'), default=False)

    cover_picture_id = HiddenField()

    editor_version = HiddenField()

    def __init__(self, post=None, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category_id.choices = Category.get_list()
        self.status.choices = Post.get_status_list()
        self.set_values(post)

    def set_values(self, post):
        if not post:
            return
        self.title.data = post.title
        self.body.data = post.body
        self.extra_body.data = post.extra_body
        self.anonymous.data = post.anonymous
        self.category_id.data = post.category_id
        self.status.data = post.status
        self.cover_picture_id.data = post.cover_picture_id
        self.editor_version.data = post.editor_version
