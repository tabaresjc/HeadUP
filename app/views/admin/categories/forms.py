# -*- coding: utf8 -*-

from flask_wtf import Form
from wtforms import TextField, TextAreaField, SelectField, validators
from flask_babel import lazy_gettext, gettext
from app.models import Category
import re


class CategoryForm(Form):
    name = TextField(lazy_gettext('Name'),
                     [validators.Length(min=4, max=25),
                      validators.InputRequired()])

    slug = TextField(lazy_gettext('Slug'),
                     [validators.Length(min=4, max=25),
                      validators.InputRequired(),
                      validators.Regexp('^[-\w]+$')])

    description = TextAreaField(lazy_gettext('Description'),
                                [validators.Length(min=4, max=1024),
                                 validators.InputRequired()])

    def __init__(self, category=None, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.set_values(category)

    def set_values(self, category=None):
        if category:
            self.name.data = category.name
            self.slug.data = category.slug
            self.description.data = category.description


class TranferCatForm(Form):
    from_id = SelectField(lazy_gettext('From'), coerce=int)

    to_id = SelectField(lazy_gettext('To'), coerce=int)

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        cat_list = Category.get_list()
        self.from_id.choices = cat_list
        self.to_id.choices = cat_list

    def validate(self):
        valid = Form.validate(self)

        if self.from_id.data == self.to_id.data:
            self.to_id.errors.append(
                gettext('Please select a different category'))
            valid = False

        return valid
