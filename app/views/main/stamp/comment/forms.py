# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, validators
from flask_babel import lazy_gettext as _lg


class CommentForm(FlaskForm):
    text = TextAreaField(_lg('COMMENT_DESC'), [
        validators.Length(min=2, max=16384),
        validators.InputRequired()
    ])

    comment_id = HiddenField()

    def __init__(self, comment=None, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        if not self.is_submitted() and comment:
            self.name.text = comment.text
