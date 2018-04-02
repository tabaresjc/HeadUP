# -*- coding: utf8 -*-

from flask import render_template
import app


@app.app.route('/')
def index():
    return render_template("main/site/home.html")


@app.app.route('/latest', defaults={'page': 1})
@app.app.route('/latest/page/<int:page>')
def latest(page=1):
    return render_template("main/index.html", page=page)


@app.app.route('/lp/campaign')
def campaign():
    return render_template("main/lp/campaign.html")


@app.app.route('/policy')
def privacy_policy():
    return render_template("main/site/policy.html")


@app.app.route('/conduct')
def code_of_conduct():
    return render_template("main/site/conduct.html")
