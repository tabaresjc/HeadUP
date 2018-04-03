# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import TextAreaField, TextField, BooleanField, SelectField, \
                    HiddenField, validators
from flask_babel import get_locale
from app.models import Category, Post


class PostForm(FlaskForm):

    title = TextField([validators.Required()])
    body = TextAreaField([validators.Required()])
    extra_body = TextAreaField([validators.Required()])
    category_id = SelectField(coerce=int)
    status = SelectField(coerce=int)
    lang = SelectField([validators.Required()])
    anonymous = BooleanField(default=0)
    remain = BooleanField(default=False)
    cover_picture_id = HiddenField()
    editor_version = HiddenField()

    def __init__(self, post=None, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category_id.choices = Category.get_list()
        self.status.choices = Post.get_status_list()
        self.lang.choices = Post.get_language_list()

        if not post:
            language = str(get_locale())
            self.lang.data = language

        if not self.is_submitted() and post:
            self.title.data = post.title
            self.body.data = post.body
            self.extra_body.data = post.extra_body
            self.anonymous.data = post.anonymous
            self.category_id.data = post.category_id
            self.status.data = post.status
            self.lang.data = post.lang
            self.cover_picture_id.data = post.cover_picture_id
            self.editor_version.data = post.editor_version
