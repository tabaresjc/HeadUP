# -*- coding: utf8 -*-

from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.classy import FlaskView, route
from flask.ext.babel import lazy_gettext, gettext, refresh
from app import app
from app.models import Picture
from forms import PictureForm


class PicturesView(FlaskView):
  route_base = '/mypage/pictures'
  decorators = [login_required]

  def get(self, id):
    picture = Picture.get_by_id(id)

    return render_template('admin/pictures/show.html',
                           picture=picture)

  @route('/', methods=['POST'])
  @route('/new', methods=['GET'])
  def post(self):
    if request.method == 'POST':
      form = PictureForm()
      if form.validate_on_submit():
        f = request.files.get('file')
        picture = Picture.create()
        picture.save_file(f, current_user)
        picture.save()

        return redirect(url_for('PicturesView:get', id=picture.id))
      else:
        flash(gettext('Invalid submission, please check the messages below'), 'error')
    else:
      form = PictureForm()

    return render_template('admin/pictures/add.html', form=form, user=None)
