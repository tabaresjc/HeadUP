# -*- coding: utf8 -*-

from flask import render_template
from flask_classy import FlaskView, route


class PagesView(FlaskView):

    route_base = ''

    @route('', endpoint='index')
    def index(self):
        return render_template('main/site/home.html')


    @route('/latest', endpoint='latest')
    def latest(self, page=1):
        return render_template('main/index.html', page=page)


    @route('/lp/campaign', endpoint='campaign')
    def campaign(self):
        return render_template('main/lp/campaign.html')


    @route('/policy', endpoint='privacy_policy')
    def privacy_policy(self):
        return render_template('main/site/policy.html')


    @route('/conduct', endpoint='code_of_conduct')
    def code_of_conduct(self):
        return render_template('main/site/conduct.html')
