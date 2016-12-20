# -*- coding: utf8 -*-

from flask import render_template
from app import app


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page=1):

    return render_template("main/stamps/index.html", page=page)


@app.route('/ranking')
def ranking():

    return render_template("main/stamps/ranking.html")
