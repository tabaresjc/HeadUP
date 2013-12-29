from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, FileField, BooleanField, validators
from flask.ext.babel import lazy_gettext

class CommentForm(Form):
	body = TextAreaField(lazy_gettext('Body'), [ 
		validators.Required(), 
		validators.Length(min = 0, max = 16000)  
		])