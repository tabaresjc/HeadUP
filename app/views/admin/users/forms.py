# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import BooleanField, TextField, TextAreaField, PasswordField, SelectField, validators
from flask_babel import lazy_gettext as _lg
import pytz
import config
from app.models import Role


def get_timezones():
    tz = []
    for c in pytz.all_timezones:
        tz.append((c, c))
    return tz


class UserForm(FlaskForm):
    email = TextField(_lg('Email'), [
        validators.Required(),
        validators.Email(),
        validators.Length(min=10, max=255)
    ])

    name = TextField(_lg('Name'), [
        validators.Required(),
        validators.Length(min=3, max=255)
    ])

    nickname = TextField(_lg('Nickname'), [
        validators.Required(),
        validators.Length(min=0, max=64)
    ])

    role_id = SelectField(_lg('Role'), [
        validators.Optional()],
        choices=Role.DEFAULT_USER_ROLES)

    password = PasswordField(_lg('Password'), [
        validators.Optional(),
        validators.EqualTo('confirm_password', message=_lg('Please repeat the password')),
        validators.Length(min=6, max=64)
    ])

    confirm_password = PasswordField(_lg('Confirm'), [validators.Optional()])

    address = TextAreaField(_lg('Address'), [validators.Length(min=0, max=255)])

    phone = TextField(_lg('Phone'), [validators.Length(min=0, max=64)])

    timezone = SelectField('Timezone', choices=get_timezones())

    def __init__(self, user=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.timezone.data = config.DEFAULT_TIMEZONE
        if not self.is_submitted() and user:
            self.email.data = user.email
            self.name.data = user.name
            self.nickname.data = user.nickname
            self.role_id.data = user.role_id
            self.address.data = user.address
            self.phone.data = user.phone
            self.timezone.data = user.timezone
