# -*- coding: utf8 -*-

from flask import render_template
import app


@app.app.errorhandler(401)
def internal_error_401(error):
    return render_template('main/common/401.html', title=error), 401


@app.app.errorhandler(403)
def internal_error_403(error):
    return render_template('main/common/403.html', title=error), 403


@app.app.errorhandler(404)
def internal_error_404(error):
    return render_template('main/common/404.html', title=error), 404


@app.app.errorhandler(500)
def internal_error_500(error):
    return render_template('main/common/500.html', title=error), 500

@app.app.errorhandler(Exception)
def internal_error_500(error):
    return render_template('main/common/500.html', title=error), 500
