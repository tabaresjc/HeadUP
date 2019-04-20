# -*- coding: utf8 -*-

from flask import render_template, redirect, url_for
from flask_login import current_user, login_required
from flask_classy import FlaskView, route


class MyPageView(FlaskView):
    route_base = '/mypage'
    decorators = [login_required]

    @route('', endpoint='dashboard')
    def index(self, page=1):
        user = current_user

        limit = 10
        posts, total = user.get_user_posts(page=page, limit=limit)

        if not posts and page > 1:
            return redirect(url_for('dashboard'))

        return render_template("admin/index.html",
                               posts=posts,
                               page=page,
                               limit=limit,
                               total=total)

    @route('/settings', endpoint='user_settings')
    def user_settings(self):
        user = current_user

        return redirect(url_for('UsersView:put', id=user.id))
