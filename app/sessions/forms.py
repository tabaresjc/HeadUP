from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators
from flask.ext.babel import lazy_gettext, gettext
from app.users.models import User

class LoginForm(Form):
	email = TextField(lazy_gettext('Email'), [ validators.Email() , validators.Length(min = 10, max = 255)])
	password = PasswordField(lazy_gettext('Password'), [ validators.Required() ])		
	remember_me = BooleanField('remember_me', default = False)

class SignUpForm(Form):
	email = TextField(lazy_gettext('Email'), [ validators.Email() , validators.Length(min = 10, max = 255)])
	name = TextField(lazy_gettext('Name'), [ validators.Required() ])
	nickname = TextField(lazy_gettext('Nickname'), [ validators.Required() ])
	password = PasswordField(lazy_gettext('Password'), [ 
		validators.Required(), 
		validators.EqualTo('confirm_password', message=lazy_gettext('Passwords must match')),
		validators.Length(min = 10, max = 64)
	])	
	confirm_password = PasswordField(lazy_gettext('Confirm'), [ validators.Required() ])

	def validate(self):
		valid = True
		if not Form.validate(self):
			valid = False

		if self.name.data != User.make_valid_name(self.name.data):
			self.name.errors.append(gettext('This name has invalid characters'))
			valid = False

		if self.nickname.data != User.make_valid_nickname(self.nickname.data):
			self.nickname.errors.append(gettext('This nickname has invalid characters'))
			valid = False

		if User.is_email_taken(self.email.data):
			self.email.errors.append(gettext('This email is already in use. Please choose another one.'))
			valid = False			

		if User.is_nickname_taken(self.nickname.data):
			self.nickname.errors.append(gettext('This nickname is already in use. Please choose another one.'))
			valid = False
		return valid