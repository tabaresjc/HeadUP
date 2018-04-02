# -*- coding: utf8 -*-

from flask import render_template
import app


@app.app.route('/ranking')
def ranking():

    return render_template('main/stamp/ranking.html')
