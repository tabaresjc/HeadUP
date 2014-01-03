from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask.ext.login import current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form
from flask.ext.babel import lazy_gettext, gettext
from app import app, login_manager
from flask.ext.paginate import Pagination
from app.comments.models import Comment

class CommentsView(FlaskView):
    route_base = '/comments'
    decorators = [login_required]

    def index(self):
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        limit = 10
        comments, count = Comment.pagination(page=page, limit=limit)

        pagination = Pagination(page=page, 
            per_page= limit, 
            total= count, 
            record_name= gettext('posts'), 
            alignment = 'right', 
            bs_version= 3)

        
        return render_template('admin/comments/index.html', 
            title = gettext('Comments | %(page)s', page=page),
            comments = comments,
            pagination = pagination)

    def get(self,id):
        comment = Comment.get_by_id(id)
        if comment is None:
            flash(gettext('The comment was not found'), 'error')
            return redirect(url_for('CommentsView:index'))

        return render_template('admin/comments/show.html', 
            title = gettext('Comment %(id)s', id=comment.id),
            comment = comment)

    @route('/', methods = ['POST'])
    @route('/new', methods = ['GET'])    
    def post(self):
    	return "ok"

    @route('/<int:id>', methods = ['PUT'])
    @route('/edit/<int:id>', methods = ['GET', 'POST'])
    def put(self, id):
    	return "ok"

    @route('/<int:id>', methods = ['DELETE'])
    @route('/remove/<int:id>', methods = ['POST'])
    def delete(self,id):
    	return "ok"
