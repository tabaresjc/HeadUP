from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField, FileField, BooleanField, validators
from flask.ext.babel import lazy_gettext, gettext


class SearchForm(Form):
	searchtext = TextField(lazy_gettext('Search'), [ validators.Required() ])