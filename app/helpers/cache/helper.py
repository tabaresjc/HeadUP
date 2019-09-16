# -*- coding: utf8 -*-

from flask_caching import Cache
from flask_caching import make_template_fragment_key


class CacheHelper(Cache):

    _cache_enabled = False

    def __init__(self, app, **kwargs):

        if app is None:
            raise ValueError("`app` must be an instance Flask")

        config = app.config.get('CACHE_CONFIG') or {}

        self._cache_enabled = app.config.get('CACHE_ENABLED', False) is True

        if not self._cache_enabled:
            config['CACHE_TYPE'] = 'null'

        super(CacheHelper, self).__init__(app=app,
                                          config=config,
                                          **kwargs)

    def get_fragment(self, name, vary_on=None):
        key = make_template_fragment_key(name, vary_on=vary_on or [])
        return self.get(key)

    def get(self, *args, **kwargs):
        # only when cache is enabled via config
        if not self._cache_enabled:
            return None

        return super(CacheHelper, self).get(*args, **kwargs)

    def set(self, *args, **kwargs):
        # only when cache is enabled via config
        if not self._cache_enabled:
            return None

        return super(CacheHelper, self).set(*args, **kwargs)

    def add(self, *args, **kwargs):
        # only when cache is enabled via config
        if not self._cache_enabled:
            return None

        return super(CacheHelper, self).add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Proxy function for internal cache object."""
        if not self._cache_enabled:
            return None

        return super(CacheHelper, self).delete(*args, **kwargs)
