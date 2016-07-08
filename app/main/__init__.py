# -*- coding: utf8 -*-

from app import app
from . import welcome  # noqa
from . import stamp  # noqa

# import route for stamp resource
app.register_blueprint(stamp.mod)
