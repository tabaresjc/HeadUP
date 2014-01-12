from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, BooleanField, SelectField, validators
from flask.ext.babel import lazy_gettext, gettext
from app.categories.models import Category
from models import Post


class PostForm(Form):
    title = TextField(lazy_gettext('Title'), [validators.Required()])
    body = TextAreaField(lazy_gettext('Body'), [validators.Required()])
    image_url = TextField(lazy_gettext('Featured Image'))
    slug = TextField(lazy_gettext('Slug'), [validators.Required()])
    category_id = SelectField(u'Category', coerce=int)
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.category_id.data = 1
        self.category_id.choices = Category.get_list()
    
    def validate(self):
        valid = True
        if not Form.validate(self):
            valid = False
        
        if Post.get_by_slug(self.slug.data):
            self.to_id.errors.append(gettext('Please select a different slug'))
            valid = False

        return valid


class EditPostForm(Form):
    title = TextField(lazy_gettext('Title'), [validators.Required()])
    body = TextAreaField(lazy_gettext('Body'), [validators.Required()])
    image_url = TextField(lazy_gettext('Featured Image'))
    remain = BooleanField(lazy_gettext('Show Post'), default=True)
    slug = TextField(lazy_gettext('Slug'), [validators.Required()])
    category_id = SelectField(u'Category', coerce=int)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.category_id.data = 1
        self.category_id.choices = Category.get_list()
    
    def validate(self):
        valid = True
        if not Form.validate(self):
            valid = False
        
        if Post.get_by_slug(self.slug.data):
            self.to_id.errors.append(gettext('Please select a different slug'))
            valid = False

        return valid

class NewPostForm(EditPostForm):
    def __init__(self, post, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.title.data = post.title
        self.body.data = post.body
        self.image_url.data = post.image_url
        self.slug.data = post.slug
        self.category_id.data = post.category_id
        self.category_id.choices = Category.get_list()
