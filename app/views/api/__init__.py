# -*- coding: utf8 -*-

import app

# Register the URLs of each module

# register the picture module
from pictures import PicturesApiView  # noqa
PicturesApiView.register(app.app)

# register the story module
from stories import StoriesApiView  # noqa
StoriesApiView.register(app.app)

# register the category module
from categories import CategoriesApiView  # noqa
CategoriesApiView.register(app.app)

# register the category module
from users import UsersApiView  # noqa
UsersApiView.register(app.app)

# register the sessions module
from sessions import SessionsApiView  # noqa
SessionsApiView.register(app.app)

# register the oembed module
from oembed import OEmbedApiView  # noqa
OEmbedApiView.register(app.app)
