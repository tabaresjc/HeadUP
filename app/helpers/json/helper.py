# -*- coding: utf8 -*-

from flask import request, json, Response, flash, redirect


class JsonHelper(object):

    @classmethod
    def redirect_or_json(cls, url, type, message=''):
        if request.is_xhr:
            if message:
                result = [{"result": "error", "message": message,
                          "type": "category", "redirect": url}]
            else:
                result = [{"result": "ok", "type": "category",
                          "redirect": url}]
            return Response(json.dumps(result), mimetype='application/json')
        else:
            if message:
                flash(message, 'error')
            return redirect(url)
