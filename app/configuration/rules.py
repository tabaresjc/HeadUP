# -*- coding: utf8 -*-

import config
import app

app.app.add_url_rule('/%s/<path:name>' % config.UPLOAD_MEDIA_PICTURES,
                 endpoint='pictures')
