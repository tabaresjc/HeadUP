from flask import render_template, flash, redirect
from app import app
from forms import LoginForm

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
        return redirect('/index')    
    return render_template('signin.html', 
        title = 'Sign In',
        form = form)    