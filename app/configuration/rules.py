# -*- coding: utf8 -*-

from app import app
import config

app.add_url_rule('/%s/<path:name>' % config.UPLOAD_MEDIA_PICTURES,
                 endpoint='pictures')
