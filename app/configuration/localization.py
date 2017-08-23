# -*- coding: utf8 -*-

from app import babel
from flask import request
from flask_login import current_user
import config

DEFAULT_LANGUAGE = 'en'
DEFAULT_TIMEZONE = 'Asia/Tokyo'


@babel.localeselector
def get_locale():
    cfg = config.__dict__

    LANGUAGES = cfg.get('LANGUAGES')

    if not LANGUAGES:
        return cfg.get('DEFAULT_LANGUAGE', DEFAULT_LANGUAGE)

    host = request.headers.get('HOST')

    for key, value in LANGUAGES.iteritems():
        if host.startswith(key):
            return key

    return request.accept_languages.best_match(config.LANGUAGES.keys())


@babel.timezoneselector
def get_timezone():
    cfg = config.__dict__

    if current_user and current_user.timezone:
        return current_user.timezone

    return cfg.get('DEFAULT_TIMEZONE', DEFAULT_TIMEZONE)
