# -*- coding: utf8 -*-

import app
from . import index  # noqa
from . import stamp  # noqa

# import route for stamp resource
app.app.register_blueprint(stamp.mod)
