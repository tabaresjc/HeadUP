# -*- coding: utf8 -*-

from flask import render_template
from app import app


@app.route('/ranking')
def ranking():

    return render_template('main/stamp/ranking.html')
