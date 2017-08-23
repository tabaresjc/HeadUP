# -*- coding: utf8 -*-

from flask_wtf import Form
from wtforms import TextField, TextAreaField, SelectField, validators
from flask_babel import lazy_gettext, gettext
from app.models import Category


class CategoryForm(Form):
    name = TextField(lazy_gettext('Name'), [validators.Required()])
    slug = TextField(lazy_gettext('Slug'), [validators.Required()])
    description = TextAreaField(lazy_gettext('Description'), [
        validators.Length(min=0, max=255)
    ])


class NewCategoryForm(CategoryForm):

    def __init__(self, category, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.name.data = category.name
        self.slug.data = category.slug
        self.description.data = category.description


class TranferCatForm(Form):
    from_id = SelectField(lazy_gettext('From'), coerce=int,
                          description=lazy_gettext('From'))
    to_id = SelectField(lazy_gettext('To'), coerce=int,
                        description=lazy_gettext('To'))

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        cat_list = Category.get_list()
        self.from_id.choices = cat_list
        self.to_id.choices = cat_list

    def validate(self):
        valid = True
        if not Form.validate(self):
            valid = False

        if self.from_id.data == self.to_id.data:
            self.to_id.errors.append(
                gettext('Please select a different category'))
            valid = False

        return valid

    def get_errors(self):
        message = u''
        for field in self.errors:
            message += '<br/>'.join(self.errors[field])
        return message
