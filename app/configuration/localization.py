# -*- coding: utf8 -*-

from flask import request
from flask_login import current_user
import app
import config

DEFAULT_LANGUAGE = 'en'
DEFAULT_TIMEZONE = 'Asia/Tokyo'
LANGUAGES = config.__dict__.get('LANGUAGES')

@app.babel.localeselector
def get_locale():
    cfg = config.__dict__

    if cfg.get('FORCE_LANG'):
        return cfg.get('FORCE_LANG')

    if not LANGUAGES:
        return cfg.get('DEFAULT_LANGUAGE', DEFAULT_LANGUAGE)

    host = request.headers.get('HOST', '')

    for key, _ in LANGUAGES.iteritems():
        if host.startswith(key):
            return key

        if u'_' in key:
            territory = key.lower().split('_').pop()

            if host.startswith(territory):
                return key

    return request.accept_languages.best_match(config.LANGUAGES.keys())


@app.babel.timezoneselector
def get_timezone():
    cfg = config.__dict__

    if current_user and current_user.timezone:
        return current_user.timezone

    return cfg.get('DEFAULT_TIMEZONE', DEFAULT_TIMEZONE)
