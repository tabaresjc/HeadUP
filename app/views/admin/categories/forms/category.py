# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, validators
from flask_babel import lazy_gettext as _lg


class CategoryForm(FlaskForm):
    slug = TextField(_lg('CATEGORY_SLUG'), [validators.Length(min=2, max=200)])
    name = TextField(_lg('CATEGORY_NAME'), [validators.Length(min=2, max=100), validators.InputRequired()])
    description = TextAreaField(_lg('CATEGORY_DESC'), [validators.Length(min=2, max=4096), validators.InputRequired()])

    name_es = TextField('Name (Spanish)', [validators.Length(max=100)])
    description_es = TextAreaField('Descripcion (Spanish)', [validators.Length(max=4096)])

    name_fr = TextField('Name (French)', [validators.Length(max=100)])
    description_fr = TextAreaField('Descripcion (French)', [validators.Length(max=4096)])

    name_ja = TextField('Name (Japanese)', [validators.Length(max=100)])
    description_ja = TextAreaField('Descripcion (Japanese)', [validators.Length(max=4096)])

    name_cn = TextField('Name (Chinese)', [validators.Length(max=100)])
    description_cn = TextAreaField('Descripcion (Chinese)', [validators.Length(max=4096)])

    def __init__(self, category=None, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        if self.is_submitted():
            return

        if category:
            self.slug.data = category.slug
            self.name.data = category.name
            self.description.data = category.description

            self.name_es.data = category.name_es
            self.description_es.data = category.description_es

            self.name_fr.data = category.name_fr
            self.description_fr.data = category.description_fr

            self.name_ja.data = category.name_ja
            self.description_ja.data = category.description_ja

            self.name_cn.data = category.name_cn
            self.description_cn.data = category.description_cn
