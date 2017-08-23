# -*- coding: utf8 -*-

from app import app
from jinja2 import evalcontextfilter
import config


@app.template_filter()
@evalcontextfilter
def replace_host_name(eval_ctx, value):
    if not value or not config.MAIN_DOMAIN:
        return value

    if config.MAIN_DOMAIN in value:
        return value

    for domain in config.OTHER_DOMAINS:
        if domain in value:
            value = value.replace(domain, config.MAIN_DOMAIN)
            break

    return value
