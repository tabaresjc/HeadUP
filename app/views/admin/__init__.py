# -*- coding: utf8 -*-

import index
import app

# register the Category module
from categories.index import CategoriesView  # noqa
CategoriesView.register(app.app)

# register the Post module
from posts.index import PostsView  # noqa
PostsView.register(app.app)

# register the User module
from users.index import UsersView  # noqa
UsersView.register(app.app)

# register the sessions module blueprint
from sessions.index import mod as sessionsModule  # noqa
app.app.register_blueprint(sessionsModule, url_prefix='/members')
