from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, FileField, BooleanField, validators

class PostForm(Form):
	title = TextField('Title', [ validators.Required() ])    
	body = TextAreaField('Body', [ validators.Required() ])
	image_url = TextField('Featured Image')


class EditPostForm(Form):
	title = TextField('Title', [ validators.Required() ])    
	body = TextAreaField('Body', [ validators.Required() ])
	image_url = TextField('Featured Image')
	remain = BooleanField('Show Post', default = True)

class NewPostForm(EditPostForm):
	def __init__(self, post, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.title.data = post.title
		self.body.data = post.body
		self.image_url.data = post.image_url


