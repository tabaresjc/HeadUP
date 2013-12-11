from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators


class LoginForm(Form):
		email = TextField('Email', [ validators.Required() ])    
		password = PasswordField('Password', [ validators.Required() ])		
		remember_me = BooleanField('remember_me', default = False)
