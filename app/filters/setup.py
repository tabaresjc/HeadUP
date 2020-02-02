# -*- coding: utf8 -*-

from app.helpers import PaginationHelper
from flask_babel import get_locale
import app
import config
import datetime


@app.app.context_processor
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
