# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import PasswordField, HiddenField, validators
from flask_babel import lazy_gettext as _lg


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_lg('USER_RESET_PASSWORD'), [
        validators.Required(),
        validators.EqualTo('confirm_password', message=_lg(
            'USER_CONFIRM_PASSWORD_INVALID')),
        validators.Length(min=10, max=64)
    ])
    confirm_password = PasswordField(
        _lg('USER_RESET_PASSWORD_CONFIRM'), [validators.Required()])
    code = HiddenField()

    def __init__(self, user=None, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

        if not self.is_submitted() and user:
            self.code.data = user.reset_password
