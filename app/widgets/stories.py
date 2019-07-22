# -*- coding: utf8 -*-

from flask import render_template
import app


@app.wg.widget('story_list')
def story_list(category_id=0, limit=20):

    return render_template('widgets/stories/_list.html',
                           category_id=category_id,
                           limit=limit)


@app.wg.widget('header_ga')
def header_ga(language='en'):
    key = u'header_ga.%s' % (language)

    fragment = app.cache.get(key)

    if not fragment:
        fragment = render_template('widgets/header/_ga.html',
                                   language=language)
        app.cache.set(key, fragment, 3600 * 24)

    return fragment
