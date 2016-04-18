from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, BooleanField, SelectField, validators
from flask.ext.babel import lazy_gettext, gettext
from app.categories.models import Category
from models import Post


class PostForm(Form):
    title = TextField(lazy_gettext('Title'), [validators.Required()])
    body = TextAreaField(lazy_gettext('Body'), [validators.Required()])
    category_id = SelectField(u'Category', coerce=int)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.category_id.data = 1
        self.category_id.choices = Category.get_list()

    def validate(self):
        if not Form.validate(self):
            return False
        return True


class EditPostForm(Form):
    title = TextField(lazy_gettext('Title'), [validators.Required()])
    body = TextAreaField(lazy_gettext('Body'), [validators.Required()])
    remain = BooleanField(lazy_gettext('Show Post'), default=True)
    category_id = SelectField(u'Category', coerce=int)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.id = kwargs.get('id') if kwargs.get('id') else 0
        self.category_id.choices = Category.get_list()

    def validate(self):
        if not Form.validate(self):
            return False
        return True

class NewPostForm(EditPostForm):
    def __init__(self, post, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.title.data = post.title
        self.body.data = post.body
        self.category_id.data = post.category_id
        self.category_id.choices = Category.get_list()
