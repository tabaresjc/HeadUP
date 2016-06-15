from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask.ext.login import current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.babel import gettext
from flask.ext.paginate import Pagination
from models import Post
from forms import PostForm, EditPostForm, NewPostForm


class PostsView(FlaskView):
    route_base = '/posts'
    decorators = [login_required]

    def index(self):
        form = PostForm()
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        limit = 5
        posts, count = Post.pagination(page=page, limit=limit)

        pagination = Pagination(page=page,
                                per_page=limit,
                                total=count,
                                record_name=gettext('posts'),
                                alignment='right',
                                bs_version=3)

        return render_template('admin/posts/index.html',
                               title=gettext('Posts | %(page)s', page=page),
                               form=form,
                               posts=posts,
                               pagination=pagination)

    def get(self, id):
        post = Post.get_by_id(id)
        if post is None:
            flash(gettext('The post was not found'), 'error')
            return redirect(url_for('PostsView:index'))

        return render_template('admin/posts/show.html',
                               title=post.title,
                               post=post)

    @route('/', methods=['POST'])
    @route('/new', methods=['GET'])
    def post(self):
        form = PostForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    post = Post.create()
                    form.populate_obj(post)
                    post.user = current_user
                    post.save()

                    flash(gettext('Post succesfully created'))
                    return redirect(url_for('PostsView:index'))
                except:
                    flash(gettext('Error while creating the post'), 'error')
            else:
                flash(
                    gettext('Invalid submission, please check the message below'), 'error')
        return render_template('admin/posts/add.html',
                               title=gettext('Create Post'),
                               form=form)

    @route('/<int:id>', methods=['PUT'])
    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        post = Post.get_by_id(id)
        if post is None:
            flash(gettext('The post was not found'), 'error')
            return redirect(url_for('PostsView:index'))
        if not current_user.is_admin() and not post.is_mine():
            abort(401)

        if request.method in ['POST', 'PUT']:
            form = EditPostForm(id=id)
            if form.validate_on_submit():
                try:
                    form.populate_obj(post)
                    post.save()
                    flash(gettext('Post was succesfully saved'))
                    if request.method == 'POST':
                        if form.remain.data:
                            return redirect(url_for('PostsView:get', id=post.id))
                        else:
                            return redirect(url_for('PostsView:index'))
                except:
                    flash(gettext('Error while updating the post'), 'error')
            else:
                flash(
                    gettext('Invalid submission, please check the message below'), 'error')

            if request.method == 'PUT':
                return jsonify(redirect_to=url_for('PostsView:index'))
        else:
            form = NewPostForm(post)
        return render_template('admin/posts/edit.html',
                               title=gettext(
                                   'Edit Post: %(title)s', title=post.title),
                               form=form,
                               post=post)

    @route('/<int:id>', methods=['DELETE'])
    @route('/remove/<int:id>', methods=['POST'])
    def delete(self, id):
        post = Post.get_by_id(id)
        if post is None:
            flash(gettext('The post was not found'), 'error')
            return redirect(url_for('PostsView:index'))
        if not post.can_edit():
            abort(401)

        try:
            title = post.title
            Post.delete(post.id)
            flash(gettext('The post "%(title)s" was removed', title=title))
        except:
            flash(gettext('Error while removing the post'), 'error')

        if request.method == 'POST':
            return redirect(url_for('PostsView:index'))
        return jsonify(redirect_to=url_for('PostsView:index'))
