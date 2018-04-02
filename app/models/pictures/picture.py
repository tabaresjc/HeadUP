# -*- coding: utf8 -*-

from flask_login import current_user
from flask import url_for
from app import sa
from app.helpers import ModelHelper, MutableObject
from config import UPLOAD_MEDIA_PICTURES_PATH
import datetime
import os


class Picture(sa.Model, ModelHelper):

    __tablename__ = 'pictures'

    __json_meta__ = ['id', 'image_url', 'user_id']

    id = sa.Column(sa.Integer, primary_key=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE', onupdate='NO ACTION'))

    attr = sa.Column(MutableObject.get_column())

    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):  # pragma: no cover
        return '<Picture %r>' % (self.id)

    def save_file(self, fileObj, user=None):
        sa.session.begin(subtransactions=True)
        try:
            import hashlib
            extension = fileObj.filename.split('.')[-1]

            h = hashlib.new('md5')
            h.update(fileObj.filename)
            h.update(datetime.datetime.utcnow().isoformat())

            self.extension = extension.lower()
            self.name = u'%s.%s' % (h.hexdigest(), self.extension)
            # associate this picture with the user
            self.user_id = user.id if user else None
            sa.session.add(self)

            # attempt to save the file
            fileObj.save(os.path.join(UPLOAD_MEDIA_PICTURES_PATH, self.name))

            # is not saved yet!
            self.save()
        except Exception as e:
            sa.session.rollback()
            raise e

    def remove(self, commit=True):
        os.remove(os.path.join(UPLOAD_MEDIA_PICTURES_PATH, self.name))
        Picture.delete(self.id, commit=commit)

    @property
    def image_url(self):
        return url_for('pictures', name=self.name)

    @property
    def name(self):
        return self.get_attribute('name', '')

    @name.setter
    def name(self, value):
        return self.set_attribute('name', value)

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
