# -*- coding: utf8 -*-

from flask import render_template
import app


@app.wg.widget('lp_home')
def lp_home(language='en'):
    key = u'lp_home.%s' % (language)

    fragment = app.cache.get(key)

    if not fragment:
        fragment = render_template('widgets/pages/_lp_home.html',
                                   language=language)
        app.cache.set(key, fragment, 3600 * 24 * 7)

    return fragment


@app.wg.widget('lp_head')
def lp_head(language='en'):
    key = u'lp_head.%s' % (language)

    fragment = app.cache.get(key)

    if not fragment:
        fragment = render_template('widgets/pages/_lp_head.html',
                                   language=language)
        app.cache.set(key, fragment, 3600 * 24)

    return fragment
