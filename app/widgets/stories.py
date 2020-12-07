# -*- coding: utf8 -*-

from flask import render_template
from app.models import Category
import app


@app.wg.widget('story_list')
def story_list(category_id=0, limit=20):

    return render_template('widgets/stories/_list.html',
                           category_id=category_id,
                           limit=limit)


@app.wg.widget('story_list_by_category')
def story_list_by_category(language='en', category_slug=None):
    if not category_slug:
        return ''

    key = u'story_list_by_category.%s.%s' % (language, category_slug)

    fragment = app.cache.get(key)

    if not fragment:
        stories, category = Category.get_posts_by_cat(category_slug, limit=3)
        fragment = render_template('widgets/stories/_list_by_category.html',
                                   category=category,
                                   stories=stories,
                                   language=language)
        app.cache.set(key, fragment, 3600)

    return fragment


@app.wg.widget('header_scripts')
def header_scripts(language='en'):
    key = u'header_scripts.%s' % (language)

    fragment = app.cache.get(key)

    if not fragment:
        fragment = render_template('widgets/header/_scripts.html',
                                   language=language)
        app.cache.set(key, fragment, 3600 * 24)

    return fragment
