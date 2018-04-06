# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, validators
from flask_babel import lazy_gettext as _lg


class ForgotPasswordForm(FlaskForm):
    email = TextField(_lg('USER_EMAIL'), [validators.Email(), validators.Length(min=10, max=255)])
