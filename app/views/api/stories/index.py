# -*- coding: utf8 -*-

from flask import url_for, request
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Post, Feed


class ApiStoriesView(FlaskView):
    route_base = '/api/stories'
    decorators = [login_required]

    @route('/item/<int:id>', methods=['GET'])
    def item(self, id):
        try:
            story = Post.get_by_id(id)

            if story is None or story.is_hidden:
                raise Exception('Story not found')

            return render_json(story=story)
        except Exception as e:
            return render_json(status=False, message=e.message)

    @route('/last-draft', methods=['GET'])
    def last_draft(self):
        try:
            draft = Post.last_draft(user_id=current_user.id)

            if draft is None:
                draft = Post.init(current_user, status=Post.POST_DRAFT_2)
                draft.save()

            return render_json(draft=draft)
        except Exception as e:
            return render_json(status=False, message=e.message)

    @route('/save-draft/<int:id>', methods=['POST'])
    def save_draft(self, id):
        try:
            data = request.values
            story = Post.get_by_id(id)

            if story is None or story.is_hidden:
                raise Exception('Story not found')

            if not story.can_edit:
                raise Exception('Your account is not allowed to perform this action')

            self.update_story(story, data, Post.POST_DRAFT_2)

            story.save()

            return render_json(story=story)
        except Exception as e:
            return render_json(status=False, message=e.message)

    @route('/publish/<int:id>', methods=['POST'])
    def publish(self, id):
        try:
            data = request.values
            story = Post.get_by_id(id)

            if story is None or story.is_hidden:
                raise Exception('Story not found')

            if not story.can_edit:
                raise Exception('Your account is not allowed to perform this action')

            self.update_story(story, data, Post.POST_PUBLIC)

            story.save()

            # refresh the cache
            # TODO: move to celery task
            Feed.clear_feed_cache()

            return render_json(story=story,
                               redirect_to=url_for('story.show', id=story.id))
        except Exception as e:
            return render_json(status=False, message=e.message)

    def update_story(self, story, data, status):
        story.title = data.get('title', u'', unicode)
        story.body = data.get('body', u'', unicode)
        story.extra_body = data.get('extra_body', u'', unicode)
        story.status = status
        story.kind = Post.KIND_STORY
