# -*- coding: utf8 -*-

from flask import request
from flask_login import current_user
from app import babel, app
import config

DEFAULT_LANGUAGE = 'en'
DEFAULT_TIMEZONE = 'Asia/Tokyo'
LANGUAGES = app.config.get('LANGUAGES') or []
LANGUAGE_KEYS = [key for key, _ in LANGUAGES]

@babel.localeselector
def get_locale():
    cfg = app.config

    if cfg.get('FORCE_LANG'):
        return cfg.get('FORCE_LANG')

    if not LANGUAGES:
        return cfg.get('DEFAULT_LANGUAGE', DEFAULT_LANGUAGE)

    host = request.headers.get('HOST', '')

    for lang in LANGUAGE_KEYS:
        if host.startswith(lang):
            return lang

        if u'_' in lang:
            territory = lang.lower().split('_').pop()

            if host.startswith(territory):
                return key

    return request.accept_languages.best_match(LANGUAGE_KEYS)


@babel.timezoneselector
def get_timezone():
    cfg = app.config

    if current_user and current_user.timezone:
        return current_user.timezone

    return cfg.get('DEFAULT_TIMEZONE', DEFAULT_TIMEZONE)
