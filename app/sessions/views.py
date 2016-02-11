# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required, user_logged_in, user_logged_out
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form
from flask.ext.babel import lazy_gettext, gettext
from app import app, login_manager

from forms import LoginForm, SignUpForm
from app.users.models import User
import datetime

mod = Blueprint('sessions', __name__)

@login_manager.user_loader
def load_user(userid):
    return User.get_by_id(userid)

@login_manager.unauthorized_handler
def unauthorized():
    session['redirect_to'] = request.url
    flash(gettext('You need to sign in or sign up before continuing.'), 'error')
    return redirect(url_for('sessions.login'))

@mod.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        flash(gettext('You are already signed in.'))
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.find_by_email(form.email.data)
            if user and user.check_password(form.password.data):
                login_user(user)
                # Update the User's info
                user.last_login = user.last_seen
                user.last_seen = datetime.datetime.utcnow()
                user.save()
                redirect_to = url_for('dashboard')
                if 'redirect_to' in session:
                    redirect_to = session['redirect_to']
                    session.pop('redirect_to', None)
                flash(gettext('Signed in successfully.'))
                return redirect(redirect_to)
            else:
                raise Exception(gettext('User not found or invalid password'))
        except:
            flash(gettext('Invalid email or password'), 'error')

    return render_template('admin/signin.html',
        title = gettext('Sign In'),
        form = form)

@mod.route('/login/comment/<int:id>')
def login_comment(id):
    session['redirect_to'] = '%s#%s' % (url_for('show_post', id=id), "create-comment")
    return redirect(url_for('sessions.login'))

@mod.route('/logout', methods = ['POST', 'DELETE'])
@login_required
def logout():
    form = Form()
    if form.validate_on_submit():
        logout_user()
        if 'redirect_to' in session:
            redirect_to = session['redirect_to']
            session.pop('redirect_to', None)
        flash(gettext('Signed out successfully.'))
    else:
        flash(gettext('Invalid Action'), 'error')

    return redirect(url_for('index'))

@mod.route('/signup', methods = ['GET', 'POST'])
def signup():
    if current_user.is_authenticated():
        flash(gettext('You are already signed in.'))
        return redirect(url_for('index'))

    form = SignUpForm()
    if form.validate_on_submit():
        try:
            ## Create user from the form
            user = User.create()

            form.populate_obj(user)
            user.set_password(form.password.data)
            user.last_seen = datetime.datetime.utcnow()
            user.last_login = datetime.datetime.utcnow()
            ## Store in database
            user.save()
            ## Login User
            login_user(user)
            flash(gettext('Welcome! You have signed up successfully.'))
            return redirect(url_for('index'))
        except:
            flash(gettext('Error while saving the new user, please retry later'), 'error')

    return render_template('admin/signup.html',
        title = gettext('Sign Up'),
        form = form)
