# -*- coding: utf8 -*-

from app import app
import index

# register the Category module
from categories.index import CategoriesView  # noqa
CategoriesView.register(app)

# register the Post module
from posts.index import PostsView  # noqa
PostsView.register(app)

# register the User module
from users.index import UsersView  # noqa
UsersView.register(app)

# register the sessions module blueprint
from sessions.index import mod as sessionsModule  # noqa
app.register_blueprint(sessionsModule, url_prefix='/members')
