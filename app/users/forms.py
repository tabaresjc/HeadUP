from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, TextAreaField, PasswordField, SelectField, validators

class UserForm(Form):
	email = TextField('Email', [ validators.Required(), validators.Email() , validators.Length(min = 10, max = 255)])
	name = TextField('Name', [ validators.Required(), validators.Length(min = 5, max = 255) ])
	nickname = TextField('Nickname', [ validators.Required() , validators.Length(min = 0, max = 64)])
	role = SelectField('Role', [validators.Optional()], choices=[('1','Administrator'),('2','Writer')])
	password = PasswordField('Password', [ 
		validators.Optional(), 
		validators.EqualTo('confirm_password', message='Please repeat the password'),
		validators.Length(min = 6, max = 64)
	])
	confirm_password = PasswordField('Confirm', [ validators.Optional() ])
	address = TextAreaField('Address', [ validators.Length(min = 0, max = 255) ])
	phone = TextField('Phone', [ validators.Length(min = 0, max = 64) ])

class NewUserForm(UserForm):
	password = PasswordField('Password', [ 
		validators.Required(), 
		validators.EqualTo('confirm_password', message='Please repeat the password'),
		validators.Length(min = 6, max = 64)
	])

class EditUserForm(UserForm):

	def __init__(self, user, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.email.data = user.email
		self.name.data = user.name
		self.nickname.data = user.nickname
		self.role.data = unicode(user.role)
		self.address.data = user.address
		self.phone.data = user.phone



