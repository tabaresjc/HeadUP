# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, validators
from flask_babel import lazy_gettext as _lg, gettext as _


class CategoryForm(FlaskForm):
    name = TextField(_lg('Name'), [validators.Length(min=4, max=100), validators.InputRequired()])
    slug = TextField(_lg('Slug'), [validators.Length(min=0, max=200)])
    description = TextAreaField(_lg('Description'), [validators.Length(min=4, max=1024), validators.InputRequired()])

    def __init__(self, category=None, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        if not self.is_submitted() and category:
            self.name.data = category.name
            self.slug.data = category.slug
            self.description.data = category.description
