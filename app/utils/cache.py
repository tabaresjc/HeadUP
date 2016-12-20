# -*- coding: utf8 -*-

from flask_caching import Cache
from flask_caching import make_template_fragment_key


class CacheBase(Cache):

    def get_fragment(self, name, vary_on=None):
        key = make_template_fragment_key(name, vary_on=vary_on or [])
        return self.get(key)
