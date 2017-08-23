# -*- coding: utf8 -*-

from flask_caching import Cache
from flask_caching import make_template_fragment_key
import config


class CacheHelper(Cache):

    def get_fragment(self, name, vary_on=None):
        key = make_template_fragment_key(name, vary_on=vary_on or [])
        return self.get(key)

    @property
    def cache_mode(self):
        return getattr(config, 'CACHE_ENABLED', False)

    def get(self, *args, **kwargs):
        "Proxy function for internal cache object."
        # only when cache is enabled via config
        if not self.cache_mode:
            return None
        return Cache.get(self, *args, **kwargs)

    def set(self, *args, **kwargs):
        "Proxy function for internal cache object."
        # only when cache is enabled via config
        if not self.cache_mode:
            return None
        return Cache.set(self, *args, **kwargs)
