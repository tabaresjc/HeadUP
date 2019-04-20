# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, validators
from flask_babel import lazy_gettext as _lg


class CategoryForm(FlaskForm):
    name = TextField(_lg('CATEGORY_NAME'), [validators.Length(
        min=4, max=100), validators.InputRequired()])
    slug = TextField(_lg('CATEGORY_SLUG'), [validators.Length(min=0, max=200)])
    description = TextAreaField(_lg('CATEGORY_DESC'), [validators.Length(
        min=4, max=1024), validators.InputRequired()])

    def __init__(self, category=None, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        if not self.is_submitted() and category:
            self.name.data = category.name
            self.slug.data = category.slug
            self.description.data = category.description
