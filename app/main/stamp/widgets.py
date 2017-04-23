# -*- coding: utf8 -*-

from flask import render_template
from app import widgets, cache
from app.models import Feed


@widgets.widget('stamps_welcome')
def stamps_welcome(page=1):
    obj = Feed.get_feed_cache(page=page)

    if obj is None:
        posts, total = Feed.posts(page=page, limit=Feed.FEED_DEFAULT_LIMIT)

        obj = render_template('main/stamp/partials/_index.html',
                              posts=posts,
                              page=page,
                              limit=Feed.FEED_DEFAULT_LIMIT,
                              total=total)

        Feed.set_feed_cache(obj, page=page)

    return obj


@widgets.widget('stamps_ranking')
def stamps_ranking(page=1, limit=5):
    key = 'stamps/ranking.v1.%s.%s' % (page, limit)
    obj = cache.get(key)

    if obj is None:
        posts, total = Feed.ranking(page=page, limit=limit)

        obj = render_template('main/stamp/partials/_ranking.html',
                              posts=posts,
                              page=page,
                              limit=limit,
                              total=total)

        cache.set(key, obj, 3600)
    return obj


@widgets.widget('stamps_category')
def stamps_category(category, page=1, limit=20):
    key = 'stamps/category.v1.%s.%s.%s' % (category.id, page, limit)
    obj = cache.get(key)

    if obj is None:
        posts, total = Feed.category(category, page=page, limit=limit)

        obj = render_template('main/stamp/partials/_category.html',
                              category=category,
                              posts=posts,
                              page=page,
                              limit=limit,
                              total=total)

        cache.set(key, obj, 3600)
    return obj
