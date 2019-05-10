# -*- coding: utf8 -*-

import app

# Register the URLs of each module

# register the sessions module
from pages import PagesView  # noqa
PagesView.register(app.app)

# register the stories module
from stories import StoriesView  # noqa
StoriesView.register(app.app)

