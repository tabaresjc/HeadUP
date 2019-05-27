# -*- coding: utf8 -*-

from flask import request, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Picture, Post


class ApiPicturesView(FlaskView):
    route_base = '/api/pictures'

    @route('/item', methods=['GET'])
    def item(self):
        picture = Picture.get_by_id(id)

        if not picture:
            abort(404, 'API_ERROR_PICTURE_NOT_FOUND')

        return render_json(picture=picture)

    @route('/upload', methods=['POST'])
    @login_required
    def upload(self):
        data = request.values
        f = request.files.get('file')

        if not f:
            abort(401, 'API_ERROR_INVALID_FILE')

        picture = Picture.create()
        picture.save_file(f, current_user)

        post_id = data.get('post_id', 0, int)

        if post_id:
            post = Post.get_by_id(post_id)

            if post is None or post.is_hidden:
                abort(404, 'API_ERROR_POST_NOT_FOUND')

            if post.cover_picture:
                post.cover_picture.remove()
            post.cover_picture_id = picture.id
            # save the post
            post.save()

        return render_json(picture=picture)

    @route('/delete/<int:id>', methods=['POST'])
    @login_required
    def delete(self, id):
        picture = Picture.get_by_id(id)

        if not picture:
            abort(404, 'API_ERROR_PICTURE_NOT_FOUND')

        if not picture.can_edit:
            abort(403, 'API_ERROR_INVALID_ACCESS')

        picture.remove()

        return render_json(picture=picture)
