# -*- coding: utf8 -*-

from sqlalchemy.ext.mutable import Mutable


class MutableObject(Mutable, dict):
    @classmethod
    def get_column(cls):
        from app.helpers import DatabaseJSONEncoder
        return cls.as_mutable(DatabaseJSONEncoder)

    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableObject."

        if not isinstance(value, MutableObject):
            if isinstance(value, dict):
                return MutableObject(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()
