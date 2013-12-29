from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, FileField, BooleanField, validators
from flask.ext.babel import lazy_gettext, gettext

class PostForm(Form):
	title = TextField(lazy_gettext('Title'), [ validators.Required() ])    
	body = TextAreaField(lazy_gettext('Body'), [ validators.Required() ])
	image_url = TextField(lazy_gettext('Featured Image'))


class EditPostForm(Form):
	title = TextField(lazy_gettext('Title'), [ validators.Required() ])    
	body = TextAreaField(lazy_gettext('Body'), [ validators.Required() ])
	image_url = TextField(lazy_gettext('Featured Image'))
	remain = BooleanField(lazy_gettext('Show Post'), default = True)

class NewPostForm(EditPostForm):
	def __init__(self, post, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.title.data = post.title
		self.body.data = post.body
		self.image_url.data = post.image_url


