# -*- coding: utf8 -*-

import app

# Register the URLs for each module

# register the sessions module
from sessions import SessionsView  # noqa
SessionsView.register(app.app)

# register the User module
from mypage import MyPageView  # noqa
MyPageView.register(app.app)

# register the Category module
from categories import CategoriesView  # noqa
CategoriesView.register(app.app)

# register the Post module
from posts import PostsView  # noqa
PostsView.register(app.app)

# register the User module
from users import UsersView  # noqa
UsersView.register(app.app)
