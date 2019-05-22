# -*- coding: utf8 -*-

from flask import request, abort
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Picture, Post


class ApiPicturesView(FlaskView):
    route_base = '/api/pictures'
    decorators = [login_required]

    @route('/item', methods=['GET'])
    def item(self):
        try:
            picture = Picture.get_by_id(id)

            if not picture:
                abort(400)

            return render_json(picture=picture)
        except Exception as e:
            return render_json(status=False, message=e.message)

    @route('/upload', methods=['POST'])
    def upload(self):
        try:
            data = request.values
            f = request.files.get('file')

            if not f:
                raise Exception('file not present')

            picture = Picture.create()
            picture.save_file(f, current_user)

            post_id = data.get('post_id', 0, int)
            if post_id:
                post = Post.get_by_id(post_id)
                if not post:
                    raise Exception('post not found')

                if post.cover_picture:
                    post.cover_picture.remove()
                post.cover_picture_id = picture.id
                # save the post
                post.save()

            return render_json(picture=picture)
        except Exception as e:
            return render_json(status=False, message=e.message)

    @route('/delete/<int:id>', methods=['POST'])
    def delete(self, id):
        try:
            picture = Picture.get_by_id(id)

            if not picture:
                abort(400)

            picture.remove()

            return render_json(picture=picture)
        except Exception as e:
            return render_json(status=False, message=e.message)
