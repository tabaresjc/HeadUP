# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import BooleanField, TextField, PasswordField, validators
from flask_babel import lazy_gettext as _lg, gettext as _
from app.models import User


class LoginForm(FlaskForm):
    email = TextField(_lg('Email'), [validators.Email(), validators.Length(min=10, max=255)])
    password = PasswordField(_lg('Password'), [validators.Required()])
    remember_me = BooleanField('remember_me', default=False)


class SignUpForm(FlaskForm):
    email = TextField(_lg('Email'), [validators.Email(), validators.Length(min=10, max=255)])
    name = TextField(_lg('Name'), [validators.Required()])
    nickname = TextField(_lg('Nickname'), [validators.Required()])
    password = PasswordField(_lg('Password'), [validators.Required(), validators.Length(min=10, max=64)])
    check_tos = BooleanField('check_tos', default=False)

    def validate(self):
        valid = super(SignUpForm, self).validate()

        if self.name.data != User.make_valid_name(self.name.data):
            self.name.errors.append(_('This name has invalid characters'))
            valid = False

        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(_('This nickname has invalid characters'))
            valid = False

        if User.is_email_taken(self.email.data):
            self.email.errors.append(_('This email is already in use. Please choose another one.'))
            valid = False

        if User.is_nickname_taken(self.nickname.data):
            self.nickname.errors.append(_('This nickname is already in use. Please choose another one.'))
            valid = False

        return valid
