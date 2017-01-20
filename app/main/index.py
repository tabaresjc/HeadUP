# -*- coding: utf8 -*-

from flask import render_template
from app import app


@app.route('/')
def index():
    return render_template("main/site/home.html")


@app.route('/latest', defaults={'page': 1})
@app.route('/latest/page/<int:page>')
def latest(page=1):

    return render_template("main/index.html", page=page)


@app.route('/policy')
def privacy_policy():
    return render_template("main/site/policy.html")
