from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators


class LoginForm(Form):
	email = TextField('Email', [ validators.Required() ])    
	password = PasswordField('Password', [ validators.Required() ])		
	remember_me = BooleanField('remember_me', default = False)

class SignUpForm(Form):
	email = TextField('Email', [ validators.Required() ])
	nickname = TextField('Nickname', [ validators.Required() ])
	password = PasswordField('Password', [ 
		validators.Required(), 
		validators.EqualTo('confirm_password', message='Passwords must match') 
	])	
	confirm_password = PasswordField('Confirm', [ validators.Required() ])	
