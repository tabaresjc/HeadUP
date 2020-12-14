# -*- coding: utf8 -*-

from flask import render_template
from app.models import Category, Post
import app


@app.wg.widget('story_list')
def story_list(category_id=0, limit=20):

    return render_template('widgets/stories/_list.html',
                           category_id=category_id,
                           limit=limit)


@app.wg.widget('story_list_by_category')
def story_list_by_category(language='en', category_slugs=None):
    if not category_slugs:
        return ''

    category_ids = []

    for slug in category_slugs:
        category = Category.get_by_cat(slug)
        if category:
            category_ids.append(category.id)

    stories, count = Post.posts_by_categories(category_ids, limit=3)
    return render_template('widgets/stories/_list_by_category.html',
                           stories=stories,
                           count=count,
                           language=language)


@app.wg.widget('header_scripts')
def header_scripts(language='en'):
    key = u'header_scripts.%s' % (language)

    fragment = app.cache.get(key)

    if not fragment:
        fragment = render_template('widgets/header/_scripts.html',
                                   language=language)
        app.cache.set(key, fragment, 3600 * 24)

    return fragment
