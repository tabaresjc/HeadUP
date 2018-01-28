# -*- coding: utf8 -*-

from app import app
from app.helpers import PaginationHelper
from flask_babel import get_locale
import config
import datetime

# Setup trim and strip for blocks
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


@app.context_processor
def utility_processor():
    # Send the current date & time
    today = datetime.date.today()
    language = get_locale()

    return dict(
        pag=PaginationHelper.pag,
        today=today,
        config=config,
        language=str(language),
        site_name=config.SITE_NAME)
