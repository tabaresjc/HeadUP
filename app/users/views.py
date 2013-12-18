from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form
from app import app, login_manager


from models import User
import datetime

class UsersView(FlaskView):
    route_base = '/users'
    decorators = [login_required]

    def index(self):
    	page = 1
    	users = []
    	pagination = []
        return render_template('admin/users/index.html', 
            title = 'Posts: User %s' % page,
            users = users,
            pagination = pagination)




