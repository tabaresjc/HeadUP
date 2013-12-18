from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form
from app import app, login_manager
from flask.ext.paginate import Pagination
from storm.locals import *
from models import User
from app.posts.models import Post
import datetime

class UsersView(FlaskView):
    route_base = '/users'
    decorators = [login_required]

    def index(self):
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        limit = 5
        users, count = User.pagination(page=page, limit=limit, orderby='users.id', desc=False)
        
        pagination = Pagination(page=page, 
            per_page=limit, 
            total= count, 
            record_name='users',
            bs_version=3)

        return render_template('admin/users/index.html', 
            title = 'Users | Page %s' % page,
            users = users,
            pagination = pagination)

    def get(self,id):
        user = User.get_by_id(id)
        if user is None:
            flash('The user was not found', 'error')
            return redirect(url_for('UsersView:index'))
        
        return render_template('admin/users/show.html', 
            title = 'User\'s Profile | %s' % user.name,
            user = user)

    @route('/', methods = ['POST'])
    @route('/new', methods = ['GET'])    
    def post(self):
        return "New ok"

    @route('/<int:id>', methods = ['PUT'])
    @route('/edit/<int:id>', methods = ['GET', 'POST'])
    def put(self, id):
        return "Edit ok"

    @route('/<int:id>', methods = ['DELETE'])
    @route('/remove/<int:id>', methods = ['POST'])
    def delete(self,id):
        return "Delete ok"
