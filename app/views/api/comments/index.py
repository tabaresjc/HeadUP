# -*- coding: utf8 -*-

from flask import request, abort
from flask_classy import FlaskView, route
from flask_login import current_user, login_required
from flask_babel import gettext as _
from app.helpers import render_json
from app.models import Comment, Post


class CommentsApiView(FlaskView):
    route_base = '/api/comments'

    @route('/post/<int:post_id>/items', methods=['GET'])
    def comments_by_post(self, post_id):
        post = Post.get_by_id(post_id)

        if not post:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        comments = post.comment_list

        return render_json(comments=comments)

    @login_required
    def post(self):
        data = request.json
        post_id = data.get('post_id', 0)
        text = data.get('text', None)
        comment_id = data.get('comment_id', None)

        if not post_id or not text:
            abort(409, 'API_ERROR_INVALID_PARAMETERS')

        post = Post.get_by_id(post_id)

        if post is None or post.is_hidden:
            abort(404, 'API_ERROR_POST_NOT_FOUND')

        comment = Comment(
            user=current_user,
            post=post,
            text=text)

        if comment_id:
            comment.comment_id = comment_id

        comment.save()

        return render_json(comment=comment)


    @login_required
    def put(self, id):
        data = request.json
        text = data.get('text', None)

        if not text:
            abort(409, 'API_ERROR_INVALID_PARAMETERS')

        comment = Comment.get_by_id(id)

        if not comment:
            abort(404, 'API_ERROR_COMMENT_NOT_FOUND')

        if not comment.can_edit:
            abort(403, 'API_ERROR_OPERATION_NOT_ALLOWED')

        comment.text = text
        comment.save()

        return render_json(comment=comment)

    @login_required
    def delete(self, id):
        comment = Comment.get_by_id(id)

        if not comment:
            abort(404, 'API_ERROR_COMMENT_NOT_FOUND')

        if not comment.can_delete:
            abort(403, 'API_ERROR_OPERATION_NOT_ALLOWED')

        Comment.delete(id)

        return render_json(status=204)
