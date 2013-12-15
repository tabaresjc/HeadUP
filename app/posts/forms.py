from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, validators

class PostForm(Form):
	title = TextField('Title', [ validators.Required() ])    
	body = TextAreaField('Body', [ validators.Required() ])		

