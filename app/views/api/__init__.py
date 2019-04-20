# -*- coding: utf8 -*-

import app

# Register the URLs for each module

# register the picture module
from pictures import ApiPicturesView  # noqa
ApiPicturesView.register(app.app)

# register the story module
from stories import ApiStoriesView  # noqa
ApiStoriesView.register(app.app)
