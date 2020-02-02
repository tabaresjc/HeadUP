# -*- coding: utf8 -*-

from flask import request, abort
from flask_classy import FlaskView, route
from micawber.providers import Provider, bootstrap_basic
from app.helpers import render_json
from app import cache


class OEmbedApiView(FlaskView):
    route_base = '/api/oembed'

    @route('/item', methods=['GET'])
    @cache.cached(query_string=True, timeout=86400)
    def get(self):
        data = request.values
        url = data.get('url', '', str)

        if not url:
            abort(400)

        providers = bootstrap_basic()
        data = providers.request(url)

        return render_json(
            url=url,
            response=data)
