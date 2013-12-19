from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators


class LoginForm(Form):
	email = TextField('Email', [ validators.Email() , validators.Length(min = 10, max = 255)])
	password = PasswordField('Password', [ validators.Required() ])		
	remember_me = BooleanField('remember_me', default = False)

class SignUpForm(Form):
	email = TextField('Email', [ validators.Email() , validators.Length(min = 10, max = 255)])
	name = TextField('Name', [ validators.Required() ])
	nickname = TextField('Nickname', [ validators.Required() ])
	password = PasswordField('Password', [ 
		validators.Required(), 
		validators.EqualTo('confirm_password', message='Passwords must match'),
		validators.Length(min = 10, max = 64)
	])	
	confirm_password = PasswordField('Confirm', [ validators.Required() ])	
