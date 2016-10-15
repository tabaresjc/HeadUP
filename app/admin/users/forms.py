# -*- coding: utf8 -*-

from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, TextAreaField, PasswordField, SelectField, validators
from flask.ext.babel import lazy_gettext, gettext
from config import LANGUAGES_FORM
import pytz
import config


def get_timezones():
  tz = []
  for c in pytz.all_timezones:
    tz.append((c, c))
  return tz


class UserForm(Form):
  email = TextField(lazy_gettext('Email'), [
                    validators.Required(),
                    validators.Email(),
                    validators.Length(min=10, max=255)])

  name = TextField(lazy_gettext('Name'), [
                   validators.Required(),
                   validators.Length(min=5, max=255)])

  nickname = TextField(lazy_gettext('Nickname'), [
                       validators.Required(),
                       validators.Length(min=0, max=64)])
  role_id = SelectField(lazy_gettext('Role'), [
                        validators.Optional()],
                        choices=config.DEFAULT_USER_ROLES)

  password = PasswordField(lazy_gettext('Password'), [
      validators.Optional(),
      validators.EqualTo('confirm_password', message=lazy_gettext(
          'Please repeat the password')),
      validators.Length(min=6, max=64)])

  confirm_password = PasswordField(
      lazy_gettext('Confirm'), [validators.Optional()])

  address = TextAreaField(lazy_gettext('Address'), [
                          validators.Length(min=0, max=255)])

  phone = TextField(lazy_gettext('Phone'), [validators.Length(min=0, max=64)])

  timezone = SelectField(u'Timezone', choices=get_timezones())

  lang = SelectField(u'language', choices=config.LANGUAGES_FORM)


class NewUserForm(UserForm):

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
    self.timezone.data = config.DEFAULT_TIMEZONE

  password = PasswordField(lazy_gettext('Password'), [
      validators.Required(),
      validators.EqualTo('confirm_password', message=lazy_gettext(
          'Please repeat the password')),
      validators.Length(min=6, max=64)
  ])


class EditUserForm(UserForm):

  def __init__(self, user, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
    self.email.data = user.email
    self.name.data = user.name
    self.nickname.data = user.nickname
    self.role_id.data = unicode(user.role_id)
    self.address.data = user.address
    self.phone.data = user.phone
    self.timezone.data = user.timezone
    self.lang.data = user.lang
