# -*- coding: utf8 -*-

from flask import render_template
from flask_babel import get_locale
from app.models import Feed
import app


@app.wg.widget('story_list')
def story_list(category_id=0, limit=20):

    return render_template('widgets/stories/_list.html',
                           category_id=category_id,
                           limit=limit)
