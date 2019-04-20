# -*- coding: utf8 -*-

from flask import request
from flask_login import current_user, login_required
from flask_classy import FlaskView, route
from app.helpers import render_json
from app.models import Picture


class ApiPicturesView(FlaskView):
    route_base = '/api/pictures'
    decorators = [login_required]

    @route('/upload', methods=['POST'])
    def upload(self):
        try:
            f = request.files.get('file')

            if not f:
                raise Exception('file not present')

            picture = Picture.create()
            picture.save_file(f, current_user)

            return render_json(url=picture.image_url)
        except Exception as e:
            return render_json(status=False, message=e.message)
