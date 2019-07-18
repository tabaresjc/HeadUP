# -*- coding: utf8 -*-

from flask import url_for, request, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Post, Feed
from app import cache


class ApiStoriesView(FlaskView):
    route_base = '/api/stories'
    formatter = None

    @route('/items', methods=['GET'])
    @route('/items/<int:page>', methods=['GET'])
    @cache.memoize()
    def items(self, page=1):
        data = request.values
        limit = data.get('limit', 5, int)

        posts, total = Feed.posts(page=page,
                                  limit=limit)

        stories = map(self.clean_story, posts)

        return render_json(stories=stories,
                           total=total,
                           page=page,
                           limit=limit)

    @route('/item/<int:id>', methods=['GET'])
    def item(self, id):
        story = Post.get_by_id(id)

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        return render_json(story=story)

    @route('/last-draft', methods=['GET'])
    @login_required
    def last_draft(self):
        draft = Post.last_draft(user_id=current_user.id)

        if draft is None:
            draft = Post.init(current_user, status=Post.POST_DRAFT_2)
            draft.save()

        return render_json(draft=draft)

    @route('/save-draft/<int:id>', methods=['POST'])
    @login_required
    def save_draft(self, id):
        data = request.values
        story = Post.get_by_id(id)

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        if not story.can_edit:
            abort(403, 'API_ERROR_INVALID_ACCESS')

        self.update_story(story, data, Post.POST_DRAFT_2)

        story.save()

        return render_json(story=story)

    @route('/publish/<int:id>', methods=['POST'])
    @login_required
    def publish(self, id):
        data = request.values
        story = Post.get_by_id(id)

        if story is None or story.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        if not story.can_edit:
            abort(403, 'API_ERROR_INVALID_ACCESS')

        self.update_story(story, data, Post.POST_PUBLIC)

        story.save()

        # refresh the cache
        # TODO: move to celery task
        Feed.clear_feed_cache()

        return render_json(story=story,
                           redirect_to=url_for('story.show', id=story.id))

    def update_story(self, story, data, status):
        story.title = data.get('title', u'', unicode)
        story.body = data.get('body', u'', unicode)
        story.extra_body = data.get('extra_body', u'', unicode)
        story.category_id = data.get('category_id', Post.CATEGORY_NONE, int)
        story.status = status
        story.kind = Post.KIND_STORY
        story.anonymous = data.get('anonymous', 0, int)

    def clean_story(self, story):
        if story.anonymous:
            story.user = None
        return story
