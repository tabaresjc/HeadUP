# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import SelectField
from flask_babel import lazy_gettext as _lg, gettext as _
from app.models import Category


class TranferForm(FlaskForm):
    from_id = SelectField(_lg('From'), coerce=int)
    to_id = SelectField(_lg('To'), coerce=int)

    def __init__(self, *args, **kwargs):
        super(TranferForm, self).__init__(*args, **kwargs)
        cat_list = Category.get_list()
        self.from_id.choices = cat_list
        self.to_id.choices = cat_list

    def validate(self):
        valid = super(TranferForm, self).validate()

        if self.from_id.data == self.to_id.data:
            self.to_id.errors.append(_('Please select a different category'))
            valid = False

        return valid
