from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, validators

class PostForm(Form):
	title = TextField('Title', [ validators.Required() ])    
	body = TextAreaField('Body', [ validators.Required() ])

class PostEditForm(Form):
	title = TextField('Title', [ validators.Required() ])    
	body = TextAreaField('Body', [ validators.Required() ])

	def __init__(self, post, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.title.data = post.title
		self.body.data = post.body