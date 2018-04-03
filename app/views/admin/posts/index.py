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
                                          limit=limit)

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
        post = Post.get_by_id(id)

        if post is None or not post.can_edit():
            return render_view(url_for('PostsView:index'),
                               status=False,
                               redirect=True,
                               message=_('POST_NOT_FOUND'))

        return render_view('admin/posts/show.html',
                           post=post)

    @route('/new', methods=['GET', 'POST'])
    def post(self):
        form = PostForm()

        if form.validate_on_submit():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                remain = request.values.get('remain', False, bool)
                post = Post.create()
                form.populate_obj(post)
                post.user = current_user

                f = request.files.get('file')

                if f:
                    picture = Picture.create()
                    picture.save_file(f, current_user)
                    post.cover_picture_id = picture.id if picture else 0

                # init the score
                post.update_score(page_view=1)

                post.editor_version = 1
                post.save()

                Feed.clear_feed_cache()

                if post.is_draft:
                    message = _('POST_DRAFT_SAVE_SUCESS')
                else:
                    message = _('POST_PUBLIC_SAVE_SUCESS')

                if remain:
                    url = url_for('PostsView:put', id=post.id, remain='y')
                else:
                    url = url_for('PostsView:get', id=post.id)

                return render_view(url, redirect=True, message=message)

            except Exception as e:
                flash(e.message, 'error')

        return render_view('admin/posts/edit.html',
                           form=form)

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        post = Post.get_by_id(id)

        if post is None or not post.can_edit() or post.is_hidden:
            return render_view(url_for('PostsView:index'),
                               status=False,
                               redirect=True,
                               message=_('POST_NOT_FOUND'))

        form = PostForm(post=post)

        if form.is_submitted():
            try:
                if not form.validate():
                    raise Exception(_('ERROR_INVALID_SUBMISSION'))

                cover_picture_id = request.values.get('cover_picture_id', 0, int)
                is_draft = request.values.get('status', 0, int) == Post.POST_DRAFT
                remain = request.values.get('remain', False, bool)

                if post.cover_picture and cover_picture_id == 0:
                    # remove the picture, when user request its deletion
                    post.cover_picture.remove()

                form.populate_obj(post)

                f = request.files.get('file')

                if f:
                    if post.cover_picture:
                        post.cover_picture.remove()
                    picture = Picture.create()
                    picture.save_file(f, current_user)
                    post.cover_picture_id = picture.id if picture else 0

                if is_draft:
                    post.status = Post.POST_DRAFT
                else:
                    if post.save_count == 1 or post.created_at is None:
                        post.created_at = Post.current_date()
                        post.save_count = 1
                    post.status = Post.POST_PUBLIC
                    post.save_count += 1

                post.editor_version = 1
                post.save()

                Feed.clear_feed_cache()

                if post.is_draft:
                    message = _('POST_DRAFT_SAVE_SUCESS')
                else:
                    message = _('POST_PUBLIC_SAVE_SUCESS')

                if not remain:
                    return render_view(url_for('PostsView:get', id=post.id),
                                       redirect=True,
                                       message=message)
            except Exception as e:
                flash(e.message, 'error')

        return render_view('admin/posts/edit.html',
                           form=form,
                           post=post)

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
