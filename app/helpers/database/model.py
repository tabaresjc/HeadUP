# -*- coding: utf8 -*-

import app
import datetime


class ModelHelper(object):

    @property
    def created_at_fmt(self):
        if not hasattr(self, 'created_at'):
            return None

        d = getattr(self, 'created_at')

        return self.format_date(d)

    @property
    def modified_at_fmt(self):
        if not hasattr(self, 'modified_at'):
            return None

        d = getattr(self, 'modified_at')

        return self.format_date(d)

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        app.sa.session.add(self)
        if commit:
            if hasattr(self, 'modified_at'):
                setattr(self, 'modified_at', datetime.datetime.utcnow())
            app.sa.session.commit()
        return self

    def set_attribute(self, key, value):
        self.attr = self.attr or {}
        if not key:
            return
        self.attr[key] = value

    def get_attribute(self, key, default=None):
        self.attr = self.attr or {}
        if not key:
            return default
        return self.attr.get(key, default)

    def format_date(self, date, fmt='DATE'):
        if not hasattr(self, '_formatter'):
            from app import app
            self._formatter = app.jinja_env.filters.get('datetimeformat')
        return self._formatter(None, date, fmt)

    @classmethod
    def begin_transaction(cls):
        app.sa.session.begin(subtransactions=True)

    @classmethod
    def commit_transaction(cls):
        app.sa.session.commit()

    @classmethod
    def rollback_transaction(cls):
        app.sa.session.rollback()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        if hasattr(instance, 'created_at'):
            setattr(instance, 'created_at', datetime.datetime.utcnow())
        if hasattr(instance, 'modified_at'):
            setattr(instance, 'modified_at', datetime.datetime.utcnow())
        return instance

    @classmethod
    def delete(cls, id, commit=True):
        cls.query.filter_by(id=id).delete()
        if commit:
            app.sa.session.commit()
        return True

    @classmethod
    def count(cls):
        return app.sa.session.query(cls).count()

    @classmethod
    def pagination(cls, limit=10, page=1, orderby='id', desc=True):
        query = cls.query
        count = query.count()
        records = []
        if count:
            sort_by = '%s %s' % (orderby, 'DESC' if desc else 'ASC')
            records = query.order_by(app.sa.text(sort_by)).limit(
                limit).offset((page - 1) * limit)
        return records, count
