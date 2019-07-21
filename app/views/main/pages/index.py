# -*- coding: utf8 -*-

from flask import render_template
from flask_classy import FlaskView, route


class PagesView(FlaskView):

    route_base = ''

    @route('', endpoint='index')
    def index(self):
        return render_template('main/pages/home.html')

    @route('/latest', endpoint='latest')
    def latest(self):
        return render_template('main/pages/latest.html')

    @route('/policy', endpoint='privacy_policy')
    def privacy_policy(self):
        return render_template('main/pages/policy.html')

    @route('/conduct', endpoint='code_of_conduct')
    def code_of_conduct(self):
        return render_template('main/pages/conduct.html')
