# -*- coding: utf8 -*-

from flask import flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from flask_babel import gettext as _
from app.models import Post, Picture, Feed
from app.helpers import render_view
from forms import PostForm


class PostsView(FlaskView):
    route_base = '/mypage/stories'
    decorators = [login_required]

    def index(self):
        page = request.values.get('page', 1, type=int)
        limit = 10

        posts, total = Post.posts_by_user(current_user.id,
                                          page=page,
                                          limit=limit,
                                          status=Post.POST_PUBLIC)

        return render_view('admin/posts/index.html',
                           posts=posts,
                           page=page,
                           limit=limit,
                           total=total)

    @route('/drafts', methods=['GET'])
    def draft_list(self):
        page = request.values.get('page', 1, type=int)
        limit = 10

        posts, total = Post.posts_by_user(current_user.id,
                                          page=page,
                                          limit=limit,
                                          status=Post.POST_DRAFT)

        return render_view('admin/posts/drafts.html',
                           posts=posts,
                           page=page,
                           limit=limit,
                           total=total)

    def get(self, id):
        return render_view(url_for('story.show', id=id), redirect=True)

    @route('/new', methods=['GET', 'POST'])
    def post(self):
        return render_view(url_for('.story.new'), redirect=True)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        return render_view(url_for('story.edit', id=id), redirect=True)

    @route('/remove/<int:id>', methods=['POST'])
    def delete(self, id):
        post = Post.get_by_id(id)

        if post is None:
            return render_view(url_for('PostsView:index'),
                               status=False,
                               redirect=True,
                               message=_('POST_NOT_FOUND'))

        if not post.can_edit():
            abort(401)

        try:
            title = post.title
            Post.delete(post.id)
            Feed.clear_feed_cache()
            ret = request.values.get('return')

            flash(_('POST_DELETE_SUCESS', title=title))

            if ret:
                return render_view(ret, redirect=True)
        except Exception as e:
            flash(_('ERROR_POST_DELETE_FAILED', error=e), 'error')

        return render_view(url_for('PostsView:index'),
                           redirect=True)
