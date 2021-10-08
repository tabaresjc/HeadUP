# -*- coding: utf8 -*-

from app.helpers import PaginationHelper
from flask_babel import get_locale
import app
import config
import datetime

# Setup trim and strip for blocks
app.app.jinja_env.trim_blocks = True
app.app.jinja_env.lstrip_blocks = True


@app.app.context_processor
def utility_processor():
    # Send the current date & time
    today = datetime.date.today()
    utc_now = datetime.datetime.utcnow()

    return dict(
        pag=PaginationHelper.pag,
        today=today,
        utc_now=utc_now,
        config=config,
        language=read_and_parse_locale(),
        site_name=config.SITE_NAME)


def read_and_parse_locale():
    lang = str(get_locale())

    if u'_' in lang:
        lang = lang.lower().split('_').pop()

    return lang.lower()
