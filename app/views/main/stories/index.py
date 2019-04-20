# -*- coding: utf8 -*-

from flask import render_template, redirect, abort
from flask_login import login_required
from flask_classy import FlaskView, route
from app.models import Post


class StoriesView(FlaskView):
    route_base = '/stories'

    @route('/new')
    @login_required
    def new(self):

        return render_template('main/story/edit.html',
                               id=0,
                               post=None)

    @route('/edit/<int:id>')
    @login_required
    def edit(self, id):

        post = Post.get_by_id(id)

        if post is None or post.is_hidden:
            abort(404)

        return render_template('main/story/edit.html',
                               id=id,
                               post=post)
