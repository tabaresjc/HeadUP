# -*- coding: utf8 -*-

from flask import request
import urllib3
import config
import json


def verify_captcha():
    if not config.RC_SECRET_KEY:
        return True

    recaptcha = request.values.get('g-recaptcha-response')

    url = "https://www.google.com/recaptcha/api/siteverify"

    params = {
        'secret': config.RC_SECRET_KEY,
        'response': recaptcha,
        'remoteip': request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    }

    http = urllib3.PoolManager()
    r = http.request('GET', url, params)

    if r.status != 200:
        return False

    data = json.loads(r.data.decode('utf-8'))

    return data.get('success', False)
