# -*- coding: utf8 -*-

from flask import Blueprint
mod = Blueprint('stamp', __name__, url_prefix='/stamp')

from . import view  # noqa
