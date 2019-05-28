# -*- coding: utf8 -*-

from flask_caching import Cache
from flask_caching import make_template_fragment_key


class CacheHelper(Cache):

    def __init__(self, app, **kwargs):

        if app is None:
            raise ValueError("`app` must be an instance Flask")

        config = app.config.get('CACHE_CONFIG') or {}

        if not app.config.get('CACHE_ENABLED'):
            config['CACHE_TYPE'] = 'null'

        super(CacheHelper, self).__init__(app=app,
                                          config=config,
                                          **kwargs)

    def get_fragment(self, name, vary_on=None):
        key = make_template_fragment_key(name, vary_on=vary_on or [])
        return self.get(key)

    def get(self, *args, **kwargs):
        "Proxy function for internal cache object."
        # only when cache is enabled via config
        if not self.cache_mode:
            return None
        return super(CacheHelper, self).get(self, *args, **kwargs)

    def set(self, *args, **kwargs):
        "Proxy function for internal cache object."
        # only when cache is enabled via config
        if not self.cache_mode:
            return None
        return super(CacheHelper, self).set(self, *args, **kwargs)

    def add(self, *args, **kwargs):
        "Proxy function for internal cache object."
        # only when cache is enabled via config
        if not self.cache_mode:
            return None
        return super(CacheHelper, self).add(self, *args, **kwargs)

    @property
    def cache_mode(self):
        return self.config.get('CACHE_ENABLED')
