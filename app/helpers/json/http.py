# -*- coding: utf8 -*-

from flask.json import JSONEncoder


class HttpJsonEncoder(JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()

        if hasattr(obj, '__json_meta__'):
            data = {}
            for field in obj.__json_meta__:
                data[field] = getattr(obj, field)
            return data

        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return super(HttpJsonEncoder, self).default(obj)
