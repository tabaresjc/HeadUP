# -*- coding: utf8 -*-

import app

# Register the URLs of each module

# register the picture module
from pictures import ApiPicturesView  # noqa
ApiPicturesView.register(app.app)

# register the story module
from stories import ApiStoriesView  # noqa
ApiStoriesView.register(app.app)

# register the category module
from categories import ApiCategoriesView  # noqa
ApiCategoriesView.register(app.app)
