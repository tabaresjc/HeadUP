from flask import render_template, flash, redirect
from app import app
import datetime
from forms import LoginForm, SignUpForm
from app import database, store
from storm.locals import *

from models import User

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home',
        content = 'Hello world!')    

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Succesfully logged in')
        return redirect('/dashboard')    
    return render_template('signin.html', 
        title = 'Sign In',
        form = form)    

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User()
        
        user.email = form.email.data
        user.role = 2
        user.created_at = datetime.datetime.now()
        user.modified_at = datetime.datetime.now()
        store.add(user)
        store.commit()
        flash('Succesfully added new user')
        return redirect('/index')
        
    return render_template('signup.html', 
        title = 'Sign Up',
        form = form)   

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html",
        title = 'Dashboard',
        content = 'Administration Site')       