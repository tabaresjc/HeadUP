# -*- coding: utf8 -*-

from flask_login import current_user
from flask import url_for
from app import sa
from app.models import Base
from app.helpers import ModelHelper, MutableObject, process_image_file
import datetime
import config
import os


class Picture(Base, sa.Model, ModelHelper):

    __tablename__ = 'pictures'

    __json_meta__ = ['id', 'user_id', 'image_url', 'image_url_org',
                     'image_url_sd', 'image_url_md', 'image_url_sm']

    SIZE_SD = 1028
    SIZE_MD = 512
    SIZE_SM = 256

    id = sa.Column(sa.Integer, primary_key=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE', onupdate='NO ACTION'))

    attr = sa.Column(MutableObject.get_column())

    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):  # pragma: no cover
        return '<Picture %r>' % (self.id)

    def save_file(self, f, user=None):
        sa.session.begin(subtransactions=True)
        try:
            # associate this picture with the user
            self.user_id = user.id if user else None

            # process the image file
            process_image_file(self, f)

            # save the current session
            sa.session.add(self)
            self.save()
        except Exception as e:
            sa.session.rollback()
            raise e

    def remove(self, commit=True):
        os.remove(os.path.join(config.UPLOAD_MEDIA_PICTURES_PATH, self.name))
        Picture.delete(self.id, commit=commit)

    @property
    def image_url(self):
        return url_for('pictures', name=self.name)

    @property
    def image_url_org(self):
        return url_for('pictures', name=self.name_org)

    @property
    def image_url_sd(self):
        return url_for('pictures', name=self.name_sd)

    @property
    def image_url_md(self):
        return url_for('pictures', name=self.name_md)

    @property
    def image_url_sm(self):
        return url_for('pictures', name=self.name_sm)

    @property
    def name(self):
        return self.get_attribute('name', '')

    @name.setter
    def name(self, value):
        return self.set_attribute('name', value)

    @property
    def name_org(self):
        return self.get_attribute('name_org', '')

    @name_org.setter
    def name_org(self, value):
        return self.set_attribute('name_org', value)

    @property
    def name_sd(self):
        return self.get_attribute('name_sd', '')

    @name_sd.setter
    def name_sd(self, value):
        return self.set_attribute('name_sd', value)

    @property
    def name_md(self):
        return self.get_attribute('name_md', '')

    @name_md.setter
    def name_md(self, value):
        return self.set_attribute('name_md', value)

    @property
    def name_sm(self):
        return self.get_attribute('name_sm', '')

    @name_sm.setter
    def name_sm(self, value):
        return self.set_attribute('name_sm', value)

    @property
    def extension(self):
        return self.get_attribute('extension', '')

    @extension.setter
    def extension(self, value):
        return self.set_attribute('extension', value)

    def is_mine(self):
        return current_user.is_authenticated and self.user.id == current_user.id

    def can_edit(self):
        return current_user.is_authenticated and (self.user.id == current_user.id or current_user.is_admin)
