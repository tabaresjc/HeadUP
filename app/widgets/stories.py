# -*- coding: utf8 -*-

from flask import render_template
from flask_babel import get_locale
from app.models import Feed
import app


@app.wg.widget('stories_welcome')
def stories_welcome(page=1, limit=Feed.FEED_DEFAULT_LIMIT):
    lang = str(get_locale())

    obj = Feed.get_feed_cache(name=Feed.CACHE_WELCOME_PAGE,
                              page=page,
                              limit=limit,
                              lang=lang)

    if obj is None:
        posts, total = Feed.posts(page=page, limit=Feed.FEED_DEFAULT_LIMIT)

        obj = render_template('widgets/stories/_welcome.html',
                              posts=posts,
                              page=page,
                              limit=Feed.FEED_DEFAULT_LIMIT,
                              total=total)

        Feed.set_feed_cache(name=Feed.CACHE_WELCOME_PAGE,
                            data=obj,
                            page=page,
                            limit=limit,
                            lang=lang)

    return obj


@app.wg.widget('stories_ranking')
def stories_ranking(page=1, limit=5):
    lang = str(get_locale())

    obj = Feed.get_feed_cache(name=Feed.CACHE_RANKING_PAGE,
                              page=page,
                              limit=limit,
                              lang=lang)

    if obj is None:
        posts, total = Feed.ranking(page=page, limit=limit)

        obj = render_template('widgets/stories/_ranking.html',
                              posts=posts,
                              page=page,
                              limit=limit,
                              total=total)

        Feed.set_feed_cache(name=Feed.CACHE_RANKING_PAGE,
                            data=obj,
                            page=page,
                            limit=limit,
                            lang=lang)

    return obj


@app.wg.widget('stories_category')
def stories_category(category, page=1, limit=100):
    lang = str(get_locale())
    name = '%s-%s' % (Feed.CACHE_CATEGORY_PAGE, category.id)
    obj = Feed.get_feed_cache(name=name,
                              page=page,
                              limit=limit,
                              lang=lang)

    if obj is None:
        posts, total = Feed.category(category, page=page, limit=limit)

        obj = render_template('widgets/stories/_category.html',
                              category=category,
                              posts=posts,
                              page=page,
                              limit=limit,
                              total=total)

        Feed.set_feed_cache(name=Feed.CACHE_CATEGORY_PAGE,
                            data=obj,
                            page=page,
                            limit=limit,
                            lang=lang)
    return obj
