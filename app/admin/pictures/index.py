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
